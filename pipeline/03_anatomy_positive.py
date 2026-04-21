"""
Anatomy Positive Specialist (PA) — body transformation descriptor.
Reads E1 (Pokémon anatomy) and E2 (type vocabulary) and produces
a full body transformation description plus 2-3 short CLIP tags.
Saves outputs/prompts_parts/{id}_{type}_pa.json.
Called by batch_runner.py (Phase C, parallel).
"""

import json
import logging

import requests

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    POKEMON_DIR,
    PROMPTS_PARTS_DIR,
    TYPE_VISUAL_DIR,
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"body_transformation", "clip_tags"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are a Pokémon body transformation specialist for FLUX.1-dev image generation.
Given E1 Pokémon anatomy and E2 type visual vocabulary, describe in natural language exactly
how each body part transforms for the new type.

Return ONLY valid JSON:
{
  "body_transformation": "...",
  "clip_tags": ["...", "...", "..."]
}

Rules for body_transformation:
- Describe the appearance of EACH transformable part after transformation: color, material, texture, shape.
- Reference E2 primary colors and anatomy for the new type.
- Include new type-specific structures freely: spines, fins, crystals, flames, tendrils, armor plates, wings.
- Describe how original-type structures are REPLACED (do not just add effects on top).
- Do NOT describe pose, expression, atmosphere, or floating effects.
- Write in flowing descriptive sentences, 4-6 sentences total.
- Be specific and visual — "deep obsidian scales with glowing orange lava cracks" not "fire-like skin".

Rules for clip_tags (CRITICAL — these go to CLIP encoder, max 77 tokens total with other fields):
- Exactly 2-3 short phrases (3-5 words each) naming the most visually distinctive morphological changes.
- Focus on type-specific structures that replace original parts: materials, textures, key anatomy.
- NO colors from the Pokémon's original typing. NO pose or expression words.
- Examples: ["molten gold bulb on back", "ember-cracked charcoal skin", "lava-plated joints"]

All output in English. No explanations outside the JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(pokemon_analysis: dict, type_vocabulary: dict, target_type: str) -> dict:
    """Call Ollama to generate body transformation description.

    Args:
        pokemon_analysis: E1 output dict for this Pokémon.
        type_vocabulary: E2 output dict for the target type.
        target_type: Target type name (e.g. 'fire').

    Returns:
        Parsed JSON dict with body_transformation.

    Raises:
        RuntimeError: If the Ollama call fails or returns invalid/incomplete JSON.
    """
    name = pokemon_analysis.get("pokemon_name", "unknown")
    pid  = pokemon_analysis.get("pokemon_id", "000")
    colors = type_vocabulary.get("colors", {})

    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {name} (#{pid}) — transform to {target_type} type\n\n"
        f"=== E1 — Anatomy ===\n"
        f"Identity traits: {', '.join(pokemon_analysis.get('identity_traits', []))}\n"
        f"Original type traits to REPLACE: {', '.join(pokemon_analysis.get('original_type_traits', []))}\n"
        f"Transformable parts: {', '.join(pokemon_analysis.get('transformable_parts', []))}\n"
        f"Anchor phrases (identity features to KEEP): {' | '.join(pokemon_analysis.get('anchor_phrases', []))}\n\n"
        f"=== E2 — {target_type.capitalize()} type visual vocabulary ===\n"
        f"Primary colors: {', '.join(colors.get('primary', []))}\n"
        f"Secondary colors: {', '.join(colors.get('secondary', []))}\n"
        f"New anatomy elements: {', '.join(type_vocabulary.get('anatomy', []))}\n\n"
        f"Describe how each transformable part looks after becoming {target_type}-type."
    )

    payload = {
        "model":  OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "format": "json",
        "stream": False,
        "think":  False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama request failed for PA {name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for PA {name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in PA response for {name}/{target_type}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate body transformation description for one (Pokémon, type) combination.

    Reads E1 and E2 JSONs, calls Ollama, saves outputs/prompts_parts/{id}_{type}_pa.json.
    Skips if a valid file already exists.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The result dict saved to disk.

    Raises:
        FileNotFoundError: If E1 or E2 JSON is missing.
        RuntimeError: If all retry attempts fail.
    """
    out_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_pa.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip PA (exists): %s", out_path.name)
            return existing

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

    logger.info("PA writing: %s × %s", pokemon_id, target_type)

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = _call_ollama(pokemon_analysis, type_vocabulary, target_type)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("PA attempt %d/%d failed %s/%s: %s", attempt, _MAX_RETRIES, pokemon_id, target_type, e)
    else:
        raise RuntimeError(f"PA all {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}")

    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_PARTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("PA saved: %s", out_path.name)
    return result
