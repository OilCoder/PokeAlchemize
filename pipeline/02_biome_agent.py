"""
Biome Agent — habitat description specialist.
Generates a description of the habitat/environment where a Pokémon would live
given a specific type adaptation. Called by batch_runner.py.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert in Pokémon habitats and ecosystems.
When given a Pokémon and a target type, describe the specific environment and habitat
where that Pokémon would live if it belonged to that type. Focus on:
- Landscape features, terrain, and geography
- Weather conditions, lighting, and atmosphere
- Characteristic elements that define that type's environment
Be vivid and specific. Write 2-3 sentences. Do not mention the Pokémon's appearance."""


def generate_biome_description(pokemon: dict, target_type: str) -> str:
    """Generate a habitat description for a Pokémon adapted to a new type.

    Args:
        pokemon: Pokémon data dict with keys: id, name, types, sprite_url.
        target_type: The target type that defines the habitat (e.g. "fire").

    Returns:
        A habitat/environment description string.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build the user prompt
    # ----
    original_types = ", ".join(pokemon["types"])
    user_prompt = (
        f"Pokémon: {pokemon['name'].capitalize()} (originally {original_types} type)\n"
        f"Target type: {target_type}\n\n"
        f"Describe the habitat and environment where this {target_type} type version would live. "
        f"The environment should contrast with its original {original_types} type habitat."
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
        logger.error("biome_agent failed for %s/%s: %s", pokemon["name"], target_type, e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the description
    # ----
    return response.json()["message"]["content"].strip()
