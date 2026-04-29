"""
Move Enricher — enriches combo_data moves with English visual prompts.
For each move in docs/outputs/combo_data/{id}_{type}.json, calls Ollama to
generate name_en and visual_prompt fields used by 11_move_illustrator.py.
Skips moves that already have visual_prompt. Updates files in-place.
"""

import json
import logging
from pathlib import Path

import requests

from config import (
    COMBO_DATA_DIR,
    DOCS_DIR,
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    TYPE_VISUAL_DIR,
)

logger = logging.getLogger(__name__)

_MAX_RETRIES   = 3
_REQUIRED_KEYS = {"name_en", "visual_prompt"}

_SYSTEM_PROMPT = """You are a Pokémon game VFX artist and Pokédex illustrator.
Your task: given a signature move (name + description in Spanish) and its elemental type,
generate a visual description for a WIDE BANNER IMAGE showing only the move's visual effect.

STRICT RULES:
- The image must show ONLY the visual effect — NO characters, NO Pokémon, NO creatures, NO silhouettes.
- The effect must be identifiable: specific visual elements from the move concept (leaves, orbs, fire, etc.)
- Write in English. Be vivid and specific. Under 60 words total for visual_prompt.
- Style: Pokémon game art, Ken Sugimori illustration aesthetic, stylized 2D VFX.
- visual_prompt must be a comma-separated list of visual elements suitable for an image model.

Return ONLY valid JSON with exactly these keys:
{
  "name_en": "English translation of the move name (2-4 words)",
  "visual_prompt": "comma-separated visual elements, specific and descriptive, no characters"
}"""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(move: dict, type_name: str, type_visual: dict) -> dict:
    """Call Ollama to generate English visual prompt for one move.

    Args:
        move: Dict with 'name' and 'desc' fields from combo_data.
        type_name: Elemental type string (e.g. 'fire', 'electric').
        type_visual: Type visual vocabulary dict from types_visual/{type}.json.

    Returns:
        Dict with 'name_en' and 'visual_prompt' keys.

    Raises:
        RuntimeError: If the API call fails, returns invalid JSON, or is missing keys.
    """
    palette = type_visual.get("palette", "")
    bg      = type_visual.get("background", "")

    user_prompt = (
        f"/no_think\n"
        f"Move name (ES): {move['name']}\n"
        f"Move description (ES): {move['desc']}\n"
        f"Elemental type: {type_name}\n"
        f"Type color palette: {palette}\n"
        f"Type environment: {bg}\n"
        f"Generate name_en and visual_prompt for this move's banner image."
    )

    payload = {
        "model":  OLLAMA_MODEL,
        "system": _SYSTEM_PROMPT,
        "prompt": user_prompt,
        "format": "json",
        "stream": False,
        "think":  False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama request failed for move '{move['name']}': {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON for move '{move['name']}': {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} for move '{move['name']}': {raw[:200]}")

    return result


# ----------------------------------------
# Step 2 — Per-file enrichment
# ----------------------------------------

def _enrich_combo(combo_path: Path, type_visual: dict) -> int:
    """Enrich all moves in one combo_data file with English visual prompts.

    Skips individual moves that already have a visual_prompt. Updates the
    file in-place only if at least one move was enriched.

    Args:
        combo_path: Path to combo_data JSON file ({id}_{type}.json).
        type_visual: Type visual vocabulary dict.

    Returns:
        Number of moves enriched (0 if all already had visual_prompt).
    """
    with open(combo_path, encoding="utf-8") as f:
        combo = json.load(f)

    moves    = combo.get("moves", [])
    type_name = combo_path.stem.split("_")[1]
    enriched = 0

    for move in moves:
        if move.get("visual_prompt"):
            continue

        last_error = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                result = _call_ollama(move, type_name, type_visual)
                move["name_en"]       = result["name_en"]
                move["visual_prompt"] = result["visual_prompt"]
                enriched += 1
                logger.info("enriched: %s → %s", move["name"], move["name_en"])
                break
            except RuntimeError as e:
                last_error = e
                logger.warning(
                    "attempt %d/%d failed for '%s': %s",
                    attempt, _MAX_RETRIES, move["name"], e,
                )
        else:
            logger.error("skipping move '%s': %s", move["name"], last_error)

    if enriched:
        with open(combo_path, "w", encoding="utf-8") as f:
            json.dump(combo, f, ensure_ascii=False, indent=2)

    return enriched


# ----------------------------------------
# Step 3 — Public API
# ----------------------------------------

def run() -> None:
    """Enrich all combo_data files with English visual prompts for each move.

    Filters to combos that have a rendered transformation image (via bundle.json).
    Skips moves already enriched. Logs summary: enriched / skipped / failed.
    """
    combo_files = sorted(COMBO_DATA_DIR.glob("*.json"))
    if not combo_files:
        logger.warning("no combo_data files found in %s", COMBO_DATA_DIR)
        return

    # Only enrich combos that have a rendered image (same filter as move_illustrator)
    bundle_path = DOCS_DIR / "data" / "bundle.json"
    rendered: set[str] = set()
    if bundle_path.exists():
        with open(bundle_path, encoding="utf-8") as f:
            bundle = json.load(f)
        for pid, types in bundle.get("transformations", {}).items():
            for t in types:
                rendered.add(f"{pid}_{t}")
    combo_files = [cf for cf in combo_files if cf.stem in rendered]

    # Pre-load type visuals
    type_visuals: dict[str, dict] = {}
    for tv_path in TYPE_VISUAL_DIR.glob("*.json"):
        with open(tv_path, encoding="utf-8") as f:
            type_visuals[tv_path.stem] = json.load(f)

    logger.info("Move Enricher — %d combos to enrich", len(combo_files))

    total_enriched = total_skipped = total_failed = 0

    for cf in combo_files:
        poke_type = cf.stem.split("_")[1]
        tv = type_visuals.get(poke_type, {})
        try:
            n = _enrich_combo(cf, tv)
            total_enriched += n
            if n == 0:
                total_skipped += 1
        except Exception as e:
            logger.error("failed combo %s: %s", cf.name, e)
            total_failed += 1

    logger.info(
        "Move Enricher done — enriched: %d moves  skipped: %d combos  failed: %d",
        total_enriched, total_skipped, total_failed,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
    run()
