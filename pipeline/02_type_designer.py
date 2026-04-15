"""
Type Designer (E2) — type visual vocabulary specialist.
Defines color palette, anatomy modifications, and visual effects for each
Pokémon type. Saves data/types_visual/{type}.json.
Called by batch_runner.py (Phase B, 18 runs).
"""

import json
import logging

import requests

from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, TYPE_VISUAL_DIR

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"colors", "anatomy", "effects", "suppress_from_others"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a Pokémon art director specializing in elemental type visual design.
Your job is to define the visual vocabulary for a Pokémon type so that any Pokémon can be
reimagined in that type while keeping its identity.

Return ONLY valid JSON with exactly these keys:
{
  "colors": {
    "primary":   ["2-3 dominant colors for this type, e.g. deep blue, aquamarine"],
    "secondary": ["1-2 accent colors, e.g. white foam, silver"],
    "avoid":     ["2-3 colors strongly associated with opposing types to remove"]
  },
  "anatomy": ["4-6 physical body modifications typical of this type, e.g. webbed feet, dorsal fins, smooth wet scales"],
  "effects": ["3-5 visual effects characteristic of this type, e.g. water droplets, ripple aura, foam spray"],
  "suppress_from_others": ["3-5 traits from other types that must be removed, e.g. flames, leaf appendages, rock texture"]
}

Focus on what a Ken Sugimori artist would draw. Be anatomically specific. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(type_name: str, morph_traits: str) -> dict:
    """Call Ollama to define the visual vocabulary for a Pokémon type.

    Args:
        type_name: The elemental type name (e.g. 'fire', 'water').
        morph_traits: Existing morph trait hints from types.json.

    Returns:
        Parsed JSON dict with colors, anatomy, effects, suppress_from_others.

    Raises:
        RuntimeError: If the Ollama API call fails, returns invalid JSON,
                      or response is missing required keys.
    """
    user_prompt = (
        f"/no_think\n"
        f"Type: {type_name}\n"
        f"Known morph traits: {morph_traits}\n"
        f"Define the full visual vocabulary for this type."
    )

    payload = {
        "model":  OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "format": "json",
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama request failed for type '{type_name}': {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for type '{type_name}': {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in Ollama response for type '{type_name}': {raw[:200]}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(type_obj: dict) -> dict:
    """Define visual vocabulary for a type and save to data/types_visual/{type}.json.

    Skips if a valid file already exists (all required keys present).
    Retries up to _MAX_RETRIES times on empty or malformed responses.

    Args:
        type_obj: Dict with keys name and morph_traits.

    Returns:
        The visual vocabulary dict saved to disk.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    type_name = type_obj["name"]
    out_path  = TYPE_VISUAL_DIR / f"{type_name}.json"

    # Skip only if file is valid (has required keys)
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip (exists): %s", out_path.name)
            return existing
        logger.warning("regenerating incomplete file: %s", out_path.name)

    logger.info("designing type: %s", type_name)

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            vocabulary = _call_ollama(type_name, type_obj.get("morph_traits", ""))
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("attempt %d/%d failed for %s: %s", attempt, _MAX_RETRIES, type_name, e)
    else:
        raise RuntimeError(f"All {_MAX_RETRIES} attempts failed for type '{type_name}': {last_error}")

    vocabulary["type_name"] = type_name

    TYPE_VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, indent=2, ensure_ascii=False)

    logger.info("saved: %s", out_path.name)
    return vocabulary
