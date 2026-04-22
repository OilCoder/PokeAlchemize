"""
Prompt Conciliator (E3) — assembles specialist outputs into final Z-Image prompt.
Reads types.json for palette/skin_material/accent and PA's signature_feature for the
Pokémon-specific line. Assembles palette-first prompt required by Z-Image-Turbo.
Saves outputs/prompts/{id}_{type}.json.
Called by batch_runner.py (Phase C, after parallel specialists).
"""

import json
import logging

from config import (
    POKEMON_DIR,
    PROMPTS_DIR,
    PROMPTS_PARTS_DIR,
    TYPE_VISUAL_DIR,
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"prompt"}
_PART_SUFFIXES = ("pa", "ps", "pe", "na", "ns")


def _load_type_visual(target_type: str) -> dict:
    """Load E2 visual vocabulary for a type from types_visual/{type}.json.

    Args:
        target_type: Type name (e.g. 'fire').

    Returns:
        E2 output dict with palette, skin_material, accent and other fields.

    Raises:
        FileNotFoundError: If the E2 file for this type does not exist.
    """
    path = TYPE_VISUAL_DIR / f"{target_type}.json"
    if not path.exists():
        raise FileNotFoundError(f"E2 missing for type '{target_type}': {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------
# Step 1 — Prompt assembly
# ----------------------------------------

def _assemble(pokemon_analysis: dict, parts: dict, target_type: str, type_data: dict) -> dict:
    """Assemble specialist outputs into a palette-first Z-Image prompt.

    Palette must come first (~50 tokens) to override Z-Image's canonical color
    priors before attention decays. Pokemon-specific signature_feature from PA
    personalizes the prompt beyond the generic type template.

    Args:
        pokemon_analysis: E1 output dict (pokemon_name field).
        parts: Dict mapping suffix → parsed JSON (pa, ps, pe, na, ns).
        target_type: Target type name (e.g. 'fire').
        type_data: Entry from types.json with palette, skin_material, accent.

    Returns:
        Dict with 'prompt' string.
    """
    name      = pokemon_analysis.get("pokemon_name", "").capitalize()
    palette   = type_data["palette"]
    skin      = type_data["skin_material"]
    accent    = type_data["accent"]
    signature = parts["pa"].get("signature_feature", "")

    prompt_parts = [
        f"Color palette: {palette}.",
        f"{name} {target_type} type. Ken Sugimori style, cel-shaded, bold black outlines, white background.",
        skin + ".",
    ]
    if signature:
        prompt_parts.append(signature)
    prompt_parts.append(f"{accent}. White background, no text.")

    return {"prompt": " ".join(prompt_parts)}


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Assemble specialist outputs into a Z-Image prompt JSON for one (Pokémon, type) combo.

    Reads E1 JSON, PA part JSON, and types.json. Skips if a valid file already exists.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The result dict saved to disk.

    Raises:
        FileNotFoundError: If E1 or any specialist part JSON is missing.
        KeyError: If target_type is not found in types.json.
    """
    out_path = PROMPTS_DIR / f"{pokemon_id}_{target_type}.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip E3 (exists): %s", out_path.name)
            return existing

    # ----
    # Substep 2.1 — Load E1
    # ----
    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")
    with open(e1_path, encoding="utf-8") as f:
        pokemon_analysis = json.load(f)

    # ----
    # Substep 2.2 — Load specialist parts
    # ----
    parts = {}
    for suffix in _PART_SUFFIXES:
        part_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_{suffix}.json"
        if not part_path.exists():
            raise FileNotFoundError(f"Part missing: {part_path}")
        with open(part_path, encoding="utf-8") as f:
            parts[suffix] = json.load(f)

    # ----
    # Substep 2.3 — Load E2 type visual vocabulary
    # ----
    type_data = _load_type_visual(target_type)

    logger.info("E3 assembling: %s × %s", pokemon_id, target_type)

    # ----
    # Substep 2.4 — Assemble and save
    # ----
    result = _assemble(pokemon_analysis, parts, target_type, type_data)
    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("E3 saved: %s", out_path.name)
    return result
