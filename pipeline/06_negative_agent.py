"""
Negative Prompt Agent — visual exclusion specialist.
Given a Pokémon, its original types, and the target type,
generates a comma-separated list of visual elements to exclude from the image.
Called by batch_runner.py for each (pokemon, target_type) combination.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at writing negative prompts for AI image generation of Pokémon.
Your task: given a Pokémon being transformed to a new type, list the visual elements that must NOT appear.
Rules:
- First: include the Pokémon's ICONIC body color(s) as specific color descriptors (e.g. "bright orange body, orange scales" for Charmander). This is the most important exclusion.
- Second: include colors, textures, and physical features specific to the original type(s)
- Third: include BIOME and environment elements from the original type (e.g. for fire: "lava, volcanic rock, ash, embers, smoldering ground")
- Fourth: include elements that would contradict the target type's visual identity
- Output only a compact comma-separated list of visual descriptors, no explanations
- Keep it under 30 items
- Examples: "bright orange body, orange scales, flames, fire, red orange coloring, lava, volcanic rock, ash ground, ember glow, heat distortion" """


def generate_negative_prompt(pokemon: dict, target_type: str) -> str:
    """Generate a negative prompt listing visual elements to exclude.

    Args:
        pokemon: Pokémon data dict with keys: id, name, types.
        target_type: The target type the Pokémon is being transformed to.

    Returns:
        A comma-separated string of visual elements to exclude.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build the user prompt
    # ----
    original_types = ", ".join(pokemon["types"])
    user_prompt = (
        f"Pokémon: {pokemon['name'].capitalize()}\n"
        f"Original type(s): {original_types}\n"
        f"Target type: {target_type}\n\n"
        f"List the visual elements from the original type(s) that must NOT appear."
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
        logger.error("negative_agent failed for %s/%s: %s", pokemon["name"], target_type, e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the negative descriptor
    # ----
    return response.json()["message"]["content"].strip()
