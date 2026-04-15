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

_REQUIRED_KEYS = {"prompt", "prompt_2", "negative", "negative_2"}
_MAX_RETRIES   = 3

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
- The Pokémon must remain RECOGNIZABLE. Use the E1 anatomy to identify its iconic features
  (e.g. Meowth's whiskers and coin, Pikachu's ears and tail, Bulbasaur's bulb).
  Those iconic features must stay — only recolor and retexture them to match the target type.
  You may add type-specific effects on top (aura, particles, glow, frost, flames) but
  do NOT replace the iconic features, do NOT add new limbs, do NOT change the silhouette.
- Propose as many visual changes as the type transformation naturally calls for —
  the goal is a convincing type reinterpretation, not a minimal tweak.
- prompt must start with: pkmnstyle, solo, white background
- prompt_2 must describe how each part of the Pokémon looks after the type transformation,
  referencing its iconic anatomy from E1
- negative must list original-type colors and icon traits as comma-separated tokens,
  and ALWAYS include: multiple creatures, two pokemon, duo, extra character, text, watermark, signature, logo
- negative_2 must suppress original colors and conflicting type elements.
  Always end with: "Only one Pokémon must appear in the image. No text, watermarks, or signatures."
- If the target type is ghost: the Pokémon body must remain SOLID and clearly visible —
  translucent or glowing is fine, but the full recognizable shape must be present.
  Ghost effects (aura, wisps, shadows) surround the body, they do NOT replace it.
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
        RuntimeError: If the Ollama API call fails, returns invalid JSON,
                      or response is missing required keys.
    """
    name = pokemon_analysis.get("pokemon_name", "unknown")
    pid  = pokemon_analysis.get("pokemon_id", "000")

    colors = type_vocabulary.get("colors", {})
    user_prompt = (
        f"/no_think\n"
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
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for {name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in Ollama response for {name}/{target_type}: {raw[:200]}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate SDXL prompt strings for one (Pokémon, type) combination.

    Reads E1 and E2 JSONs, calls Ollama, saves data/prompts/{id}_{type}.json.
    Skips if a valid file already exists (all required keys present).
    Retries up to _MAX_RETRIES times on empty or malformed responses.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The prompt dict saved to disk.

    Raises:
        FileNotFoundError: If E1 or E2 JSON is missing.
        RuntimeError: If all retry attempts fail.
    """
    out_path = PROMPTS_DIR / f"{pokemon_id}_{target_type}.json"

    # Skip only if file is valid (has required keys)
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip (exists): %s", out_path.name)
            return existing
        logger.warning("regenerating incomplete file: %s", out_path.name)

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

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            prompts = _call_ollama(pokemon_analysis, type_vocabulary, target_type)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("attempt %d/%d failed for %s/%s: %s", attempt, _MAX_RETRIES, pokemon_id, target_type, e)
    else:
        raise RuntimeError(f"All {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}")

    prompts["pokemon_id"]  = pokemon_id
    prompts["target_type"] = target_type

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

    logger.info("saved: %s", out_path.name)
    return prompts
