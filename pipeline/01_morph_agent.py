"""
Morph Agent — structural change instruction specialist.
Given a Pokémon and a target type, generates a detailed img2img instruction
describing the specific visual/structural changes needed for the transformation.
Called by batch_runner.py for each (pokemon, target_type) combination.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Stable Diffusion prompt engineer specializing in Pokémon type transformations.
Output a short list of comma-separated visual keywords describing the structural changes for the new type.

Rules:
- Output ONLY comma-separated tags. No sentences. No explanations.
- Focus on: body part changes, textures, colors, new appendages (e.g. "flame-tipped tail, magma shell, amber eyes").
- Keep the Pokémon recognizable — transform features, never remove them.
- 6 tags maximum. Each tag: 1-3 words. Direct and specific.
- Write in English."""


def generate_morph_instruction(pokemon: dict, target_type: str, morph_traits: str) -> str:
    """Generate a structural transformation instruction for img2img generation.

    Args:
        pokemon: Pokémon data dict with keys: id, name, types.
        target_type: The target type to transform the Pokémon into.
        morph_traits: Visual trait descriptors for the target type from types.json.

    Returns:
        An img2img instruction string starting with 'pkmnstyle'.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build the user prompt
    # ----
    original_types = ", ".join(pokemon["types"])
    user_prompt = (
        f"Pokémon: {pokemon['name'].capitalize()} (originally {original_types} type)\n"
        f"Target type: {target_type}\n"
        f"Type visual traits: {morph_traits}\n\n"
        f"Write the img2img instruction for this transformation."
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
        logger.error("morph_agent failed for %s/%s: %s", pokemon["name"], target_type, e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the instruction
    # ----
    return response.json()["message"]["content"].strip()
