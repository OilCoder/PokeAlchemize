"""
Prompt Writer (E3) — SDXL dual-encoder prompt specialist.
Reads E1 (Pokémon anatomy) and E2 (type vocabulary) JSONs and produces
4 strings per combination: prompt, prompt_2, negative, negative_2.
Saves data/prompts/{id}_{type}.json.
Called by batch_runner.py (Phase C, 2700 runs).
"""

import json
import logging

import requests

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    POKEMON_DIR,
    PROMPTS_DIR,
    TYPE_VISUAL_DIR,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Stable Diffusion XL prompt engineer for Pokémon sprite generation.
SDXL has two text encoders — you write a different string for each:

  prompt    → CLIP-L: short style-anchor tags, max 20 tokens, comma-separated keywords
  prompt_2  → OpenCLIP-G: natural language description of the transformed Pokémon, 40-60 words

You also write two negatives:
  negative   → CLIP-L: suppression keywords, max 15 tokens
  negative_2 → OpenCLIP-G: explicit description of what MUST NOT appear, 20-35 words,
               name each original-type body part and state its replacement
               (e.g. "tail must not have a flame, tail has a water fin instead")

Context: E1 Pokémon anatomy analysis + E2 target type visual vocabulary.

Return ONLY valid JSON with exactly these keys:
{
  "prompt":    "...",
  "prompt_2":  "...",
  "negative":  "...",
  "negative_2": "..."
}

Rules:
- prompt must start with: pkmnstyle, solo, white background
- prompt_2 must name the Pokémon and describe all visual changes in natural language
- negative must list original-type colors and icon traits as comma-separated tokens
- negative_2 must name each original-type feature and explicitly state its replacement
- All output in English. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(pokemon_analysis: dict, type_vocabulary: dict, target_type: str) -> dict:
    """Call Ollama to generate 4 SDXL prompt strings for one (Pokémon, type) combination.

    Args:
        pokemon_analysis: E1 output dict for this Pokémon.
        type_vocabulary: E2 output dict for the target type.
        target_type: Target type name (e.g. 'fire').

    Returns:
        Parsed JSON dict with prompt, prompt_2, negative, negative_2.

    Raises:
        RuntimeError: If the Ollama API call fails or returns invalid JSON.
    """
    name = pokemon_analysis.get("pokemon_name", "unknown")
    pid  = pokemon_analysis.get("pokemon_id", "000")

    colors = type_vocabulary.get("colors", {})
    user_prompt = (
        f"Pokémon: {name} (#{pid})\n"
        f"Target type: {target_type}\n\n"
        f"=== E1 — Pokémon anatomy ===\n"
        f"Identity traits: {', '.join(pokemon_analysis.get('identity_traits', []))}\n"
        f"Original type traits to replace: {', '.join(pokemon_analysis.get('original_type_traits', []))}\n"
        f"Transformable parts: {', '.join(pokemon_analysis.get('transformable_parts', []))}\n"
        f"Colors to suppress: {', '.join(pokemon_analysis.get('suppress_colors', []))}\n\n"
        f"=== E2 — Type visual vocabulary ===\n"
        f"Colors primary: {', '.join(colors.get('primary', []))}\n"
        f"Colors secondary: {', '.join(colors.get('secondary', []))}\n"
        f"Colors to avoid: {', '.join(colors.get('avoid', []))}\n"
        f"Anatomy: {', '.join(type_vocabulary.get('anatomy', []))}\n"
        f"Effects: {', '.join(type_vocabulary.get('effects', []))}\n"
        f"Suppress from others: {', '.join(type_vocabulary.get('suppress_from_others', []))}\n\n"
        f"Write the 4 SDXL prompt strings for this transformation."
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
        raise RuntimeError(f"Ollama request failed for {name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for {name}/{target_type}: {e}") from e


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate SDXL prompt strings for one (Pokémon, type) combination.

    Reads E1 and E2 JSONs, calls Ollama, saves data/prompts/{id}_{type}.json.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The prompt dict saved to disk.

    Raises:
        FileNotFoundError: If E1 or E2 JSON is missing.
        RuntimeError: If Ollama call fails.
    """
    out_path = PROMPTS_DIR / f"{pokemon_id}_{target_type}.json"
    if out_path.exists():
        logger.info("skip (exists): %s", out_path.name)
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    e2_path = TYPE_VISUAL_DIR / f"{target_type}.json"

    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")
    if not e2_path.exists():
        raise FileNotFoundError(f"E2 missing: {e2_path}")

    with open(e1_path, encoding="utf-8") as f:
        pokemon_analysis = json.load(f)
    with open(e2_path, encoding="utf-8") as f:
        type_vocabulary = json.load(f)

    logger.info("writing prompt: %s × %s", pokemon_id, target_type)
    prompts = _call_ollama(pokemon_analysis, type_vocabulary, target_type)
    prompts["pokemon_id"]  = pokemon_id
    prompts["target_type"] = target_type

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

    logger.info("saved: %s", out_path.name)
    return prompts
