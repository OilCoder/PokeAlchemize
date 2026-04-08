"""
Pokemon Agent — visual description specialist.
Generates a description of how a Pokémon would look if it belonged to a different type.
Called by batch_runner.py for each (pokemon, target_type) combination.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Stable Diffusion prompt engineer specializing in Pokémon visual design.
Output a short list of comma-separated tags describing the Pokémon's appearance for the new type.

Rules:
- Output ONLY comma-separated tags. No sentences. No explanations.
- Include: dominant body color, secondary color, key textures, defining visual traits of the type.
- Preserve iconic features of the Pokémon — recolor or retexture them, never omit them.
- 6 tags maximum. Each tag: 1-3 words. Specific color names preferred (e.g. "crimson body", "pale beige skin").
- Write in English."""


def generate_pokemon_description(pokemon: dict, target_type: str) -> str:
    """Generate a visual description of a Pokémon adapted to a new type.

    Args:
        pokemon: Pokémon data dict with keys: id, name, types, sprite_url.
        target_type: The target type to adapt the Pokémon to (e.g. "fire").

    Returns:
        A visual description string of the adapted Pokémon.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build the user prompt
    # ----
    original_types = ", ".join(pokemon["types"])
    user_prompt = (
        f"Describe how {pokemon['name'].capitalize()} (originally {original_types} type) "
        f"would look if it were a {target_type} type Pokémon."
    )

    # ----
    # Step 2 – Call Ollama API
    # ----
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "options": {"think": False},
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("pokemon_agent failed for %s/%s: %s", pokemon["name"], target_type, e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the description
    # ----
    return response.json()["message"]["content"].strip()
