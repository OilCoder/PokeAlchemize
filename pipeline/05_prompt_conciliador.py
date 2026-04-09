"""
Prompt Conciliador — consolidates morph and visual descriptions into a final prompt.
Supports two output styles controlled by config.PROMPT_STYLE:
  - "tags"      → comma-separated SD-style keywords, max 10, for SD 1.5 pipelines
  - "narrative" → 2-3 descriptive sentences in natural language, for FLUX pipelines
Called by batch_runner.py for each (pokemon, target_type) combination.
"""

import logging
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, PROMPT_STYLE

logger = logging.getLogger(__name__)

_SYSTEM_PROMPTS = {
    "tags": """You are a Stable Diffusion prompt engineer specializing in Pokémon.
Given a Pokémon's body structure, transformation tags, and visual tags for a new type,
output a single clean comma-separated prompt.

Rules:
- Output ONLY comma-separated tags. No sentences. No explanations.
- First: include 2-3 tags describing the Pokémon's body structure (shape, silhouette).
  These anchor the identity — do NOT include type-specific colors or traits here.
- Then: include the most relevant transformation tags (type colors, new textures, key features).
- Remove duplicates and contradictions between the two tag lists.
- Maximum 10 tags total. Each tag: 1-4 words.
- Write in English.""",

    "narrative": """You are an image generation prompt writer specializing in Pokémon.
Given a Pokémon's body structure, transformation tags, and visual tags for a new type,
output a short natural language description suitable for FLUX image generation.

Rules:
- Output ONLY the description. No labels, no explanations.
- Write 2-3 sentences in plain English.
- Sentence 1: describe the Pokémon's body shape and silhouette (type-neutral anchor).
- Sentence 2-3: describe the type transformation — new colors, textures, features.
- Do NOT include the Pokémon's name or type label.
- Avoid contradictions between sentences.
- Keep it under 60 words total.""",
}


def consolidate_prompt(
    pokemon: dict,
    target_type: str,
    morph_tags: str,
    pokemon_tags: str,
) -> str:
    """Consolidate morph and visual descriptions into a final prompt.

    Output format depends on config.PROMPT_STYLE:
    - "tags": comma-separated SD keywords (max 10).
    - "narrative": 2-3 natural language sentences for FLUX.

    Args:
        pokemon: Pokémon data dict with keys: id, name, types, structure.
        target_type: The target type being applied (e.g. "fire").
        morph_tags: Transformation tags or description from morph_agent.
        pokemon_tags: Visual tags or description from pokemon_agent.

    Returns:
        Consolidated prompt string in the configured style.

    Raises:
        RuntimeError: If the Ollama API call fails.
    """
    system_prompt = _SYSTEM_PROMPTS.get(PROMPT_STYLE, _SYSTEM_PROMPTS["tags"])

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
        f"Consolidate into a {'comma-separated SD prompt' if PROMPT_STYLE == 'tags' else 'natural language FLUX description'} anchored to the body structure."
    )

    # ----
    # Step 2 – Call Ollama API
    # ----
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
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
