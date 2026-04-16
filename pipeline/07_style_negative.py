"""
Style Negative Specialist (NS) — original type color and effect suppression list.
Reads E2 (type vocabulary) and produces a comma-separated list of colors,
textures, and atmospheric effects from the original type to suppress.
Saves outputs/prompts_parts/{id}_{type}_ns.json.
Called by batch_runner.py (Phase C, parallel).
"""

import json
import logging

import requests

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    POKEMON_DIR,
    PROMPTS_PARTS_DIR,
    TYPE_VISUAL_DIR,
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"negative_style"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a visual suppression specialist for FLUX.1-dev Pokémon image generation.
Given the original type's visual vocabulary, list specific colors, textures, particles,
and atmospheric effects from the ORIGINAL type that must NOT appear in the generated image.

Return ONLY valid JSON:
{
  "negative_style": "..."
}

Rules:
- List original-type colors (e.g. "bright orange glow", "fire red tones").
- List original-type atmospheric effects (e.g. "heat haze", "ember particles", "flame aura").
- List original-type lighting (e.g. "warm orange lighting", "fire glow illumination").
- Comma-separated list of short phrases, no sentences.
- 5-8 items maximum.
- All output in English. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(pokemon_analysis: dict, type_vocabulary: dict, target_type: str) -> dict:
    """Call Ollama to generate style suppression list.

    Args:
        pokemon_analysis: E1 output dict (for original type context).
        type_vocabulary: E2 output dict for the TARGET type (to get suppress_from_others).
        target_type: Target type name.

    Returns:
        Parsed JSON dict with negative_style.

    Raises:
        RuntimeError: If the Ollama call fails or returns invalid/incomplete JSON.
    """
    name = pokemon_analysis.get("pokemon_name", "unknown")
    original_types = pokemon_analysis.get("original_types", [])
    colors = type_vocabulary.get("colors", {})

    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {name} — original type(s): {', '.join(original_types)} → transforming to {target_type}\n\n"
        f"Original type suppress colors: {', '.join(pokemon_analysis.get('suppress_colors', []))}\n"
        f"Target type colors to avoid: {', '.join(colors.get('avoid', []))}\n"
        f"Effects to suppress from other types: {', '.join(type_vocabulary.get('suppress_from_others', []))}\n\n"
        f"List the colors, atmospheric effects, and lighting from the original type that must NOT appear."
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
        raise RuntimeError(f"Ollama request failed for NS {name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for NS {name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in NS response for {name}/{target_type}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate style suppression list for one (Pokémon, type) combination.

    Reads E1 and E2 JSONs, calls Ollama, saves outputs/prompts_parts/{id}_{type}_ns.json.
    Skips if a valid file already exists.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The result dict saved to disk.

    Raises:
        FileNotFoundError: If E1 or E2 JSON is missing.
        RuntimeError: If all retry attempts fail.
    """
    out_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_ns.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip NS (exists): %s", out_path.name)
            return existing

    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    e2_path = TYPE_VISUAL_DIR / f"{target_type}.json"

    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")
    if not e2_path.exists():
        raise FileNotFoundError(f"E2 missing: {e2_path}")

    with open(e1_path, encoding="utf-8") as f:
        pokemon_analysis = json.load(f)
    with open(e2_path, encoding="utf-8") as f:
        type_vocabulary = json.load(f)

    logger.info("NS writing: %s × %s", pokemon_id, target_type)

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = _call_ollama(pokemon_analysis, type_vocabulary, target_type)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("NS attempt %d/%d failed %s/%s: %s", attempt, _MAX_RETRIES, pokemon_id, target_type, e)
    else:
        raise RuntimeError(f"NS all {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}")

    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("NS saved: %s", out_path.name)
    return result
