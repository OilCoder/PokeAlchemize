"""
Anatomy Negative Specialist (NA) — original body feature suppression list.
Reads E1 (Pokémon anatomy) and produces a comma-separated list of original-type
body features that must NOT appear in the generated image.
Saves outputs/prompts_parts/{id}_{type}_na.json.
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
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"negative_anatomy"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a visual suppression specialist for FLUX.1-dev Pokémon image generation.
Given E1 original type traits, list the TYPE-SPECIFIC AESTHETICS of body features that must NOT appear.

Return ONLY valid JSON:
{
  "negative_anatomy": "..."
}

Rules:
- Suppress only the TYPE-SPECIFIC APPEARANCE of original features: their original-type color, material, or texture.
- NEVER suppress the structural shape or silhouette of a feature — only its original-type aesthetics.
  WRONG: "flame tail tip" (suppresses the whole tail feature)
  CORRECT: "orange flame on tail, fire-burning tail tip" (suppresses only the fire aesthetic of the tail)
  WRONG: "sharp teeth" (suppresses a structural identity feature)
  CORRECT: "ghostly green teeth, poison-tinted fangs" (suppresses only the type-specific color of the teeth)
- Suppress the colors and textures that are exclusive to the original type.
- NEVER include effects, particles, auras, or lighting that belong to the TARGET type.
- Comma-separated list of short phrases (2-6 words each), no full sentences.
- 5-10 items maximum.
- All output in English. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(pokemon_analysis: dict, target_type: str) -> dict:
    """Call Ollama to generate anatomy suppression list.

    Args:
        pokemon_analysis: E1 output dict for this Pokémon.
        target_type: Target type name (e.g. 'fire').

    Returns:
        Parsed JSON dict with negative_anatomy.

    Raises:
        RuntimeError: If the Ollama call fails or returns invalid/incomplete JSON.
    """
    name = pokemon_analysis.get("pokemon_name", "unknown")

    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {name} — being transformed from its original type to {target_type}\n\n"
        f"Original type traits to suppress: {', '.join(pokemon_analysis.get('original_type_traits', []))}\n"
        f"Colors tied to original type: {', '.join(pokemon_analysis.get('suppress_colors', []))}\n\n"
        f"List the body features and colors from the original type that must NOT appear."
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
        raise RuntimeError(f"Ollama request failed for NA {name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for NA {name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in NA response for {name}/{target_type}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate anatomy suppression list for one (Pokémon, type) combination.

    Reads E1 JSON, calls Ollama, saves outputs/prompts_parts/{id}_{type}_na.json.
    Skips if a valid file already exists.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The result dict saved to disk.

    Raises:
        FileNotFoundError: If E1 JSON is missing.
        RuntimeError: If all retry attempts fail.
    """
    out_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_na.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip NA (exists): %s", out_path.name)
            return existing

    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")

    with open(e1_path, encoding="utf-8") as f:
        pokemon_analysis = json.load(f)

    logger.info("NA writing: %s × %s", pokemon_id, target_type)

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = _call_ollama(pokemon_analysis, target_type)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("NA attempt %d/%d failed %s/%s: %s", attempt, _MAX_RETRIES, pokemon_id, target_type, e)
    else:
        raise RuntimeError(f"NA all {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}")

    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("NA saved: %s", out_path.name)
    return result
