"""
Prompt Conciliador — consolidates morph and visual tags into a clean SD prompt.
Receives the outputs of morph_agent and pokemon_agent plus the Pokémon's structural
description, and produces a single deduplicated prompt within the 77-token CLIP limit.
Called by batch_runner.py for each (pokemon, target_type) combination.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Stable Diffusion prompt engineer specializing in Pokémon.
Given a Pokémon's body structure, transformation tags, and visual tags for a new type,
output a single clean comma-separated prompt.

Rules:
- Output ONLY comma-separated tags. No sentences. No explanations.
- First: include 2-3 tags describing the Pokémon's body structure (shape, silhouette).
  These anchor the identity — do NOT include type-specific colors or traits here.
- Then: include the most relevant transformation tags (type colors, new textures, key features).
- Remove duplicates and contradictions between the two tag lists.
- Maximum 10 tags total. Each tag: 1-4 words.
- Write in English."""


def consolidate_prompt(
    pokemon: dict,
    target_type: str,
    morph_tags: str,
    pokemon_tags: str,
) -> str:
    """Consolidate morph and visual tags into a clean SD prompt.

    Args:
        pokemon: Pokémon data dict with keys: id, name, types, structure.
        target_type: The target type being applied (e.g. "fire").
        morph_tags: Comma-separated tags from morph_agent.
        pokemon_tags: Comma-separated tags from pokemon_agent.

    Returns:
        A clean comma-separated SD prompt string.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    # ----
    # Step 1 – Build user prompt
    # ----
    structure = pokemon.get("structure", pokemon["name"])
    user_prompt = (
        f"Pokémon: {pokemon['name']}\n"
        f"Body structure: {structure}\n"
        f"Target type: {target_type}\n"
        f"Transformation tags: {morph_tags}\n"
        f"Visual tags: {pokemon_tags}\n\n"
        f"Consolidate into a clean SD prompt anchored to the body structure."
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
        logger.error("prompt_conciliador failed for %s/%s: %s", pokemon["name"], target_type, e)
        raise RuntimeError(f"Ollama request failed: {e}") from e

    # ----
    # Step 3 – Extract and return consolidated prompt
    # ----
    return response.json()["message"]["content"].strip()
