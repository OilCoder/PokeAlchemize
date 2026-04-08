"""
Scene Conciliador — first reconciliation step.
Merges the Pokémon visual description and the biome/habitat description
into a single coherent scene description. Output is passed to style_conciliador.
Called by batch_runner.py.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at writing prompts for AI image generation.
You will receive two descriptions: one about a Pokémon's appearance and one about its habitat.
Merge them into a single, vivid scene description that places the Pokémon naturally in its environment.
Rules:
- Write one dense, flowing paragraph of 3-4 sentences
- Integrate the Pokémon and the environment seamlessly
- CRITICAL: preserve the exact body color stated in the Pokémon description — never soften or omit it
- Keep all specific visual details from both descriptions
- Do not add new elements not present in the inputs
- Output only the merged scene description, nothing else"""


def reconcile_scene(pokemon_desc: str, biome_desc: str) -> str:
    """Merge a Pokémon description and a biome description into a scene.

    Args:
        pokemon_desc: Visual description of the adapted Pokémon.
        biome_desc: Habitat/environment description for the combination.

    Returns:
        A merged scene description string.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build the user prompt
    # ----
    user_prompt = (
        f"Pokémon description:\n{pokemon_desc}\n\n"
        f"Habitat description:\n{biome_desc}\n\n"
        f"Merge these into a single scene description."
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
        logger.error("scene_conciliador failed: %s", e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return the scene description
    # ----
    return response.json()["message"]["content"].strip()
