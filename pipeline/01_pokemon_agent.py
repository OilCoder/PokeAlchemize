"""
Pokemon Agent — visual description specialist.
Generates a description of how a Pokémon would look if it belonged to a different type.
Called by batch_runner.py for each (pokemon, target_type) combination.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Pokémon visual designer specializing in type transformations.
When given a Pokémon and a target type, describe in vivid detail how that Pokémon would look
if it belonged to the target type. Focus exclusively on visual aspects:
- Body colors and patterns adapted to the new type
- New physical features, textures, or appendages the type would bring
- Changes in size, posture, or silhouette if relevant
Be specific and concrete. Write 2-3 sentences. Do not include stats, abilities, or lore."""


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
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("pokemon_agent failed for %s/%s: %s", pokemon["name"], target_type, e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the description
    # ----
    return response.json()["message"]["content"].strip()
