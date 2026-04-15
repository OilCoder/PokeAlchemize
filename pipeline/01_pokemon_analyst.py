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

SYSTEM_PROMPT = """You are a Pokémon visual anatomy expert. Your job is to analyze a Pokémon
and describe its visual structure so an artist can reimagine it with a different elemental type.

Return ONLY valid JSON with exactly these keys:
{
  "identity_traits": ["4-6 core visual features that make this Pokémon recognizable regardless of type"],
  "original_type_traits": ["3-5 visual features clearly derived from its original type(s), e.g. flame tail, leaf bulb, rock shell"],
  "transformable_parts": ["4-6 body parts that can visually express a new type, e.g. tail, shell, skin texture, back growth"],
  "suppress_colors": ["3-5 specific colors to suppress when changing type, tied to original type palette"]
}

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
        RuntimeError: If the Ollama API call fails or returns invalid JSON.
    """
    user_prompt = (
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
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for {pokemon['name']}: {e}") from e


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon: dict) -> dict:
    """Analyze Pokémon visual anatomy and save result to data/pokemon/{id}.json.

    Args:
        pokemon: Dict with keys id, name, types.

    Returns:
        The analysis dict saved to disk.

    Raises:
        RuntimeError: If the Ollama call fails.
    """
    out_path = POKEMON_DIR / f"{pokemon['id']}.json"
    if out_path.exists():
        logger.info("skip (exists): %s", out_path.name)
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    logger.info("analyzing: %s (%s)", pokemon["name"], pokemon["id"])
    analysis = _call_ollama(pokemon)
    analysis["pokemon_id"]   = pokemon["id"]
    analysis["pokemon_name"] = pokemon["name"]

    POKEMON_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info("saved: %s", out_path.name)
    return analysis
