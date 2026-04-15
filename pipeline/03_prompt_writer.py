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

_REQUIRED_KEYS = {"prompt"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """You are an expert FLUX.1-dev prompt engineer for Pokémon sprite generation.
FLUX.1-dev uses a T5-XXL text encoder that understands natural language descriptions precisely.
Write prompts as flowing descriptive sentences — NOT comma-separated keyword lists.

Context: E1 Pokémon anatomy analysis + E2 target type visual vocabulary.

Return ONLY valid JSON with exactly this key:
{
  "prompt": "..."
}

Prompt structure (follow this order):
1. Style anchor: start with exactly "pkmnstyle, solo, white background."
2. Subject line: one sentence naming the Pokémon and its new type.
3. Identity anchors: copy the E1 anchor_phrases VERBATIM — these are non-negotiable.
4. Original type suppression: for each trait in E1 original_type_traits, write an explicit
   negation using the pattern "there is no [trait], [body part] does not have [trait]".
   Example: "there is no flame on the tail, the tail does not have fire, only a crystal ice spike."
   Place this BEFORE the type transformation description so T5-XXL weighs it heavily.
5. Type transformation: describe each body part's new appearance in natural language,
   referencing E2 anatomy and effects. Be bold — change colors, textures, anatomy, and pose.
   Add type-specific body parts freely: wings, fins, crystal armor, flame mane, spectral tendrils.
6. Atmosphere: 1-2 sentences on visual effects and lighting that reinforce the type.
7. Avoidances: end with "There is only one Pokémon. No text, no watermarks, no signatures."

Writing rules:
- Use descriptive sentences, not tag lists. "Its tail ends in a sharp ice crystal spike"
  is better than "ice tail, crystal, frozen".
- Suppression: one short phrase per original trait. "no flame, tail is ice crystal only."
- Use E1 anchor_phrases verbatim — they are short by design.
- Type transformation: 2-3 sentences maximum, most important changes only.
- For ghost type: body SOLID and visible, effects surround it, do not replace it.
- STRICT total prompt length: 55-70 words maximum. Count every word. Be ruthless.
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
    anchor_phrases = pokemon_analysis.get("anchor_phrases", [])
    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {name} (#{pid})\n"
        f"Target type: {target_type}\n\n"
        f"=== E1 — Pokémon anatomy ===\n"
        f"Identity traits: {', '.join(pokemon_analysis.get('identity_traits', []))}\n"
        f"Original type traits to replace: {', '.join(pokemon_analysis.get('original_type_traits', []))}\n"
        f"Transformable parts: {', '.join(pokemon_analysis.get('transformable_parts', []))}\n"
        f"Colors to suppress: {', '.join(pokemon_analysis.get('suppress_colors', []))}\n"
        f"ANCHOR PHRASES (copy verbatim into prompt): {' | '.join(anchor_phrases)}\n\n"
        f"=== E2 — Type visual vocabulary ===\n"
        f"Colors primary: {', '.join(colors.get('primary', []))}\n"
        f"Colors secondary: {', '.join(colors.get('secondary', []))}\n"
        f"Colors to avoid: {', '.join(colors.get('avoid', []))}\n"
        f"Anatomy: {', '.join(type_vocabulary.get('anatomy', []))}\n"
        f"Effects: {', '.join(type_vocabulary.get('effects', []))}\n"
        f"Suppress from others: {', '.join(type_vocabulary.get('suppress_from_others', []))}\n\n"
        f"Write the single FLUX prompt for this transformation."
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
        raise RuntimeError(f"Ollama request failed for {name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Ollama for {name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in Ollama response for {name}/{target_type}: {raw[:200]}")

    # Hard-cap at 90 words — qwen3 ignores word-count instructions.
    # Truncate at sentence boundary to avoid cut mid-phrase.
    words = result["prompt"].split()
    if len(words) > 90:
        truncated = " ".join(words[:90])
        last_period = truncated.rfind(".")
        result["prompt"] = truncated[:last_period + 1] if last_period > 60 else truncated

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
