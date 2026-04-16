"""
Pose & Expression Specialist (PE) — body language and expression descriptor.
Reads E1 (Pokémon anatomy) and derives a pose and expression that matches
the target type's personality and energy.
Saves outputs/prompts_parts/{id}_{type}_pe.json.
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

_REQUIRED_KEYS = {"pose_expression"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a Pokémon pose and expression specialist for FLUX.1-dev image generation.
Given the Pokémon's body structure and the target type's personality, describe the pose,
body language, and facial expression.

Return ONLY valid JSON:
{
  "pose_expression": "..."
}

Type personalities — use as guide:
- fire: aggressive, forward-leaning, fierce snarl or open mouth with visible heat
- water: graceful, fluid, calm and composed, slight forward tilt
- ghost: eerie floating or hunched, hollow glowing eyes, head tilted hauntingly
- ice: rigid and still, cold direct stare, perfectly balanced defensive stance
- electric: dynamic, alert, crackling energy, wide bright eyes, one paw raised
- grass: relaxed, grounded, gentle expression, stable four-legged or natural stance
- psychic: serene, eyes glowing, slight levitation or meditative upright pose
- fighting: powerful wide stance, determined expression, arms or limbs raised ready
- rock: low heavy-footed stance, immovable, stoic expression
- ground: dominant, planted firmly, imposing forward presence
- flying: wings spread wide or raised, elevated, free expression, light landing pose
- poison: sinister low stance, sly half-lidded eyes, slight menacing lean
- bug: alert and tense, multidirectional awareness, quick crouched posture
- dragon: proud and majestic, upright imposing stance, intense gaze
- dark: menacing low crouch, sharp predatory gaze, body angled forward
- steel: rigid upright armored stance, powerful and mechanical expression
- fairy: playful and light-footed, whimsical expression, slight bounce or spin pose
- normal: relaxed neutral stance, friendly approachable expression

Rules:
- Describe the specific stance (limb positions, weight distribution, orientation).
- Describe head angle and facial expression (eyes, mouth).
- Match the type personality precisely.
- 1-2 sentences only.
- All output in English. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(pokemon_analysis: dict, target_type: str) -> dict:
    """Call Ollama to generate pose and expression description.

    Args:
        pokemon_analysis: E1 output dict for this Pokémon.
        target_type: Target type name (e.g. 'fire').

    Returns:
        Parsed JSON dict with pose_expression.

    Raises:
        RuntimeError: If the Ollama call fails or returns invalid/incomplete JSON.
    """
    name = pokemon_analysis.get("pokemon_name", "unknown")
    pid  = pokemon_analysis.get("pokemon_id", "000")

    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {name} (#{pid}) — target type: {target_type}\n\n"
        f"Body structure: {', '.join(pokemon_analysis.get('identity_traits', []))}\n"
        f"Transformable parts: {', '.join(pokemon_analysis.get('transformable_parts', []))}\n\n"
        f"Describe the pose and expression for a {target_type}-type {name}."
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
        raise RuntimeError(f"Ollama request failed for PE {name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for PE {name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in PE response for {name}/{target_type}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate pose and expression description for one (Pokémon, type) combination.

    Reads E1 JSON, calls Ollama, saves outputs/prompts_parts/{id}_{type}_pe.json.
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
    out_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_pe.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip PE (exists): %s", out_path.name)
            return existing

    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")

    with open(e1_path, encoding="utf-8") as f:
        pokemon_analysis = json.load(f)

    logger.info("PE writing: %s × %s", pokemon_id, target_type)

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = _call_ollama(pokemon_analysis, target_type)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("PE attempt %d/%d failed %s/%s: %s", attempt, _MAX_RETRIES, pokemon_id, target_type, e)
    else:
        raise RuntimeError(f"PE all {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}")

    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("PE saved: %s", out_path.name)
    return result
