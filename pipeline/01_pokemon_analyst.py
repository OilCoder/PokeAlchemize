"""
Pokémon Analyst (E1) — visual anatomy specialist.
Analyzes each Pokémon and extracts structural identity: shape, color anchors,
transformable parts, and original-type traits to suppress.
Saves data/pokemon/{id}.json. Called by batch_runner.py (Phase A, 150 runs).
"""

import json
import logging

import requests

from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, POKEMON_DIR

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"identity_traits", "original_type_traits", "transformable_parts", "suppress_colors", "anchor_phrases"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a Pokémon visual anatomy expert. Your job is to analyze a Pokémon
and describe its visual structure so an artist can reimagine it with a different elemental type.

Return ONLY valid JSON with exactly these keys:
{
  "identity_traits": ["4-6 core visual features that make this Pokémon recognizable regardless of type"],
  "original_type_traits": ["3-5 visual features clearly derived from its original type(s), e.g. flame tail, leaf bulb, rock shell"],
  "transformable_parts": ["4-6 body parts that can visually express a new type, e.g. tail, shell, skin texture, back growth"],
  "suppress_colors": ["3-5 specific colors to suppress when changing type, tied to original type palette"],
  "anchor_phrases": ["2-3 exact visual phrases that MUST appear verbatim in any generation prompt to preserve identity,
    e.g. 'gold yen coin embedded on forehead', 'curled spiral tail tip', 'bipedal stance with short arms extended outward'"]
}

anchor_phrases rules:
- Each phrase must name a SPECIFIC physical feature with its exact appearance (shape, color, placement).
- These phrases will be copied verbatim into image generation prompts — write them as precise visual descriptions.
- Prioritize the 2-3 features that most uniquely identify this Pokémon from any similar species.

Be specific and concrete. Focus on anatomy, not lore. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(pokemon: dict) -> dict:
    """Call Ollama to analyze a Pokémon's visual anatomy.

    Args:
        pokemon: Dict with keys id, name, types.

    Returns:
        Parsed JSON dict with identity_traits, original_type_traits,
        transformable_parts, suppress_colors.

    Raises:
        RuntimeError: If the Ollama API call fails, returns invalid JSON,
                      or response is missing required keys.
    """
    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {pokemon['name']} (#{pokemon['id']})\n"
        f"Original types: {', '.join(pokemon['types'])}\n"
        f"Analyze its visual anatomy for type transformation."
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
        raise RuntimeError(f"Ollama request failed for {pokemon['name']}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for {pokemon['name']}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in Ollama response for {pokemon['name']}: {raw[:200]}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon: dict) -> dict:
    """Analyze Pokémon visual anatomy and save result to data/pokemon/{id}.json.

    Skips if a valid file already exists (all required keys present).
    Retries up to _MAX_RETRIES times on empty or malformed responses.

    Args:
        pokemon: Dict with keys id, name, types.

    Returns:
        The analysis dict saved to disk.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    out_path = POKEMON_DIR / f"{pokemon['id']}.json"

    # Skip only if file is valid (has required keys)
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip (exists): %s", out_path.name)
            return existing
        logger.warning("regenerating incomplete file: %s", out_path.name)

    logger.info("analyzing: %s (%s)", pokemon["name"], pokemon["id"])

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            analysis = _call_ollama(pokemon)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("attempt %d/%d failed for %s: %s", attempt, _MAX_RETRIES, pokemon["name"], e)
    else:
        raise RuntimeError(f"All {_MAX_RETRIES} attempts failed for {pokemon['name']}: {last_error}")

    analysis["pokemon_id"]   = pokemon["id"]
    analysis["pokemon_name"] = pokemon["name"]

    POKEMON_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info("saved: %s", out_path.name)
    return analysis
