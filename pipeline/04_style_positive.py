"""
Style Positive Specialist (PS) — visual effects and atmosphere descriptor.
Reads E2 (type vocabulary) and produces a description of the visual effects,
aura, particles, and lighting that reinforce the new type.
Saves outputs/prompts_parts/{id}_{type}_ps.json.
Called by batch_runner.py (Phase C, parallel).
"""

import json
import logging

import requests

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    PROMPTS_PARTS_DIR,
    TYPE_VISUAL_DIR,
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"style_effects"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a Pokémon visual atmosphere specialist for FLUX.1-dev image generation.
Given the target type's visual vocabulary, describe the visual effects, aura, and atmosphere
surrounding the transformed Pokémon.

Return ONLY valid JSON:
{
  "style_effects": "..."
}

Rules:
- Describe type-specific particle effects (embers drifting upward, frost crystals floating, ghost wisps, sparks, etc.).
- Describe the aura: its color, intensity, and shape around the body.
- Describe lighting mood: warm amber fire glow, cold blue-white ice light, eerie purple ghost luminescence, etc.
- End with: "Clean cel-shaded Pokémon illustration style with bold outlines and soft shading."
- 2-4 sentences total.
- Be vivid and specific — describe particle behavior and light color precisely.
- All output in English. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(type_vocabulary: dict, target_type: str, pokemon_name: str) -> dict:
    """Call Ollama to generate visual style description.

    Args:
        type_vocabulary: E2 output dict for the target type.
        target_type: Target type name (e.g. 'fire').
        pokemon_name: Pokémon name for context.

    Returns:
        Parsed JSON dict with style_effects.

    Raises:
        RuntimeError: If the Ollama call fails or returns invalid/incomplete JSON.
    """
    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {pokemon_name} — {target_type} type\n\n"
        f"=== E2 — {target_type.capitalize()} type visual vocabulary ===\n"
        f"Effects: {', '.join(type_vocabulary.get('effects', []))}\n"
        f"Suppress from others: {', '.join(type_vocabulary.get('suppress_from_others', []))}\n\n"
        f"Describe the visual atmosphere and effects surrounding this {target_type}-type Pokémon."
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
        raise RuntimeError(f"Ollama request failed for PS {pokemon_name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for PS {pokemon_name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in PS response for {pokemon_name}/{target_type}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate visual style description for one (Pokémon, type) combination.

    Reads E2 JSON and E1 for pokemon name, calls Ollama, saves result.
    Skips if a valid file already exists.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The result dict saved to disk.

    Raises:
        FileNotFoundError: If E2 JSON is missing.
        RuntimeError: If all retry attempts fail.
    """
    out_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_ps.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip PS (exists): %s", out_path.name)
            return existing

    e2_path = TYPE_VISUAL_DIR / f"{target_type}.json"
    if not e2_path.exists():
        raise FileNotFoundError(f"E2 missing: {e2_path}")

    with open(e2_path, encoding="utf-8") as f:
        type_vocabulary = json.load(f)

    # Read pokemon name from E1 if available, fallback to ID
    from config import POKEMON_DIR
    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    pokemon_name = pokemon_id
    if e1_path.exists():
        with open(e1_path, encoding="utf-8") as f:
            pokemon_name = json.load(f).get("pokemon_name", pokemon_id)

    logger.info("PS writing: %s × %s", pokemon_id, target_type)

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = _call_ollama(type_vocabulary, target_type, pokemon_name)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("PS attempt %d/%d failed %s/%s: %s", attempt, _MAX_RETRIES, pokemon_id, target_type, e)
    else:
        raise RuntimeError(f"PS all {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}")

    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("PS saved: %s", out_path.name)
    return result
