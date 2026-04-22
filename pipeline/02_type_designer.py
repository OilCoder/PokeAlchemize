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

_REQUIRED_KEYS = {"colors", "anatomy", "effects", "suppress_from_others", "palette", "skin_material", "accent"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a Pokémon art director specializing in elemental type visual design for Z-Image-Turbo.
Your job is to define the visual vocabulary for a Pokémon type so that any Pokémon can be
reimagined in that type while keeping its identity.

Return ONLY valid JSON with exactly these keys:
{
  "colors": {
    "primary":   ["2-3 dominant colors for this type"],
    "secondary": ["1-2 accent colors"],
    "avoid":     ["2-3 colors from opposing types to remove"]
  },
  "anatomy": ["4-6 physical body modifications typical of this type"],
  "effects": ["3-5 visual effects characteristic of this type"],
  "suppress_from_others": ["3-5 traits from other types that must be removed"],
  "palette": "comma-separated list of 4-5 specific colors in order of dominance, e.g. 'jet black, dark gray, bright orange lava glow, crimson red, amber'",
  "skin_material": "one sentence describing how any Pokémon body surface transforms for this type, using material/texture language not color replacement — e.g. 'lava-hardened black skin with bright orange molten lava visible through surface cracks all over the body'",
  "accent": "one concise line for tail tip and eyes in this type — e.g. 'amber tail tip, ember-red eyes'"
}

Rules for palette: list colors from most dominant to least; be specific (not 'red' but 'crimson red'); max 5 colors.
Rules for skin_material: describe what the skin IS made of, not what color it changed to; keep under 20 words; no pose or atmosphere.
Rules for accent: two elements only — tail tip and eyes; one line, under 10 words.
Focus on what a Ken Sugimori artist would draw. No explanations outside the JSON."""


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
