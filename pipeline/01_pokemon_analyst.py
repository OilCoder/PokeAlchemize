"""
Pokémon Analyst (E1) — visual anatomy specialist.
Two-stage pipeline: qwen2.5vl:7b analyzes the original sprite image to extract
visual facts, then qwen3:30b uses those facts to produce the structured anatomy
output for downstream specialists.
Saves outputs/pokemon/{id}.json. Called by batch_runner.py (Phase A, 146 runs).
"""

import base64
import json
import logging
from pathlib import Path

import requests

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_VISION_MODEL,
    POKEMON_DIR,
    SPRITES_DIR,
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"identity_traits", "original_type_traits", "transformable_parts", "suppress_colors", "anchor_phrases"}
_MAX_RETRIES   = 3

# ----------------------------------------
# Step 1 — Vision: extract visual facts from sprite
# ----------------------------------------

_VISION_SYSTEM = """You are a pixel-art visual analyst. Describe what you see in this Pokémon sprite image.
Return ONLY valid JSON with exactly these keys:
{
  "body_colors": ["exact colors visible on the body, head, limbs — e.g. 'bright yellow', 'dark brown', 'pale cream'"],
  "body_parts": ["every distinct body part visible — e.g. 'rounded head', 'short stubby legs', 'pointed ears', 'curled tail tip'"],
  "body_plan": "CRITICAL — classify the locomotion type from ONLY what is visible in the sprite. Choose exactly one: 'quadruped' (four legs on ground), 'biped' (two legs, upright), 'serpentine' (snake/eel body, no legs), 'fish' (fish body, fins, no legs), 'blob' (amorphous, no clear limbs), 'floating' (hovering, no ground contact), 'insect' (six limbs or wings+legs), 'other: <describe>'",
  "silhouette": "one sentence describing the overall shape and proportions",
  "type_markers": ["visual features that suggest the original elemental type — e.g. 'flame on tail tip', 'leaf bulb on back', 'water droplets on skin'"],
  "distinctive_features": ["2-3 features unique to this specific Pokémon, not shared by similar species"]
}
CRITICAL RULES:
- For body_plan: count visible legs carefully. A serpentine or eel-shaped body with no visible legs = 'serpentine'. A flat fish body with fins = 'fish'. Do NOT assume legs exist if they are not visible.
- Be exact and literal. No lore, no names, no game knowledge. Describe only what is visually present."""


def _load_sprite_b64(pokemon_id: str) -> str:
    """Load a sprite image and return it as a base64-encoded string.

    Tries .webp first, falls back to .png.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').

    Returns:
        Base64-encoded image string.

    Raises:
        FileNotFoundError: If no sprite file exists for this Pokémon.
    """
    for ext in (".webp", ".png"):
        sprite_path = SPRITES_DIR / f"{pokemon_id}{ext}"
        if sprite_path.exists():
            return base64.b64encode(sprite_path.read_bytes()).decode("utf-8")
    raise FileNotFoundError(f"Sprite not found: {SPRITES_DIR / pokemon_id}.*")


def _call_vision(pokemon: dict) -> dict:
    """Call qwen2.5vl to extract visual facts from the Pokémon sprite.

    Args:
        pokemon: Dict with keys id, name, types.

    Returns:
        Parsed JSON dict with body_colors, body_parts, silhouette,
        type_markers, distinctive_features.

    Raises:
        RuntimeError: If the API call fails or returns invalid JSON.
    """
    sprite_b64 = _load_sprite_b64(pokemon["id"])

    payload = {
        "model":  OLLAMA_VISION_MODEL,
        "system": _VISION_SYSTEM,
        "prompt": f"/no_think\nAnalyze this Pokémon sprite. Original types: {', '.join(pokemon['types'])}.",
        "images": [sprite_b64],
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
        raise RuntimeError(f"Vision API failed for {pokemon['name']}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from vision model for {pokemon['name']}: {e}") from e


# ----------------------------------------
# Step 2 — Reasoning: produce structured anatomy JSON
# ----------------------------------------

_REASONING_SYSTEM = """You are a Pokémon visual anatomy expert. Your job is to analyze a Pokémon
and describe its visual structure so an artist can reimagine it with a different elemental type.

Return ONLY valid JSON with exactly these keys:
{
  "identity_traits": ["4-6 core visual features that make this Pokémon recognizable regardless of type"],
  "original_type_traits": ["3-5 visual features clearly derived from its original type(s), e.g. flame tail, leaf bulb, rock shell"],
  "transformable_parts": ["4-6 body parts that can visually express a new type, e.g. tail, shell, skin texture, back growth"],
  "suppress_colors": ["3-5 specific colors to suppress when changing type, tied to original type palette"],
  "anchor_phrases": ["3 exact visual phrases that MUST appear verbatim in any generation prompt to preserve identity,
    e.g. 'quadruped, four legs planted on ground, low crawling stance', 'butterfly insect, large wings spread wide, hovering in flight',
    'bipedal, upright stance, short arms extended outward', 'gold yen coin embedded on forehead', 'curled spiral tail tip'"]
}

anchor_phrases rules:
- The FIRST phrase MUST describe body plan and locomotion using the body_plan field from visual facts. This is mandatory.
  Map body_plan directly: 'quadruped' → 'quadruped, four legs on ground', 'biped' → 'bipedal, upright stance',
  'serpentine' → 'serpentine body, no limbs, elongated form', 'fish' → 'fish body, fins only, no legs',
  'blob' → 'amorphous blob body, no distinct limbs', 'floating' → 'floating body, no ground contact',
  'insect' → 'insect body, six limbs'.
  CRITICAL: if body_plan is 'serpentine' or 'fish', NEVER write 'quadruped' or 'four legs'. Trust body_plan over body_parts.
- The SECOND and THIRD phrases name specific physical features with exact appearance (shape, placement) — NO colors from the original type.
- All phrases will be copied verbatim into image generation prompts — write them as precise visual descriptions.
- Base anchor_phrases on the visual facts provided — not on general knowledge.

Be specific and concrete. Focus on anatomy, not lore. No explanations outside the JSON."""


def _call_reasoning(pokemon: dict, visual: dict) -> dict:
    """Call qwen3 to produce structured anatomy output using visual facts.

    Args:
        pokemon: Dict with keys id, name, types.
        visual: Visual description dict from _call_vision.

    Returns:
        Parsed JSON dict with all _REQUIRED_KEYS.

    Raises:
        RuntimeError: If the API call fails, returns invalid JSON,
                      or response is missing required keys.
    """
    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {pokemon['name']} (#{pokemon['id']})\n"
        f"Original types: {', '.join(pokemon['types'])}\n\n"
        f"=== Visual facts from sprite image ===\n"
        f"Body plan (locomotion type): {visual.get('body_plan', 'unknown')} ← USE THIS for anchor_phrases[0]\n"
        f"Body colors: {', '.join(visual.get('body_colors', []))}\n"
        f"Body parts: {', '.join(visual.get('body_parts', []))}\n"
        f"Silhouette: {visual.get('silhouette', '')}\n"
        f"Type markers (original type features to replace): {', '.join(visual.get('type_markers', []))}\n"
        f"Distinctive features (unique to this species): {', '.join(visual.get('distinctive_features', []))}\n\n"
        f"Use these visual facts to produce the anatomy analysis for type transformation."
    )

    payload = {
        "model":  OLLAMA_MODEL,
        "system": _REASONING_SYSTEM,
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
        raise RuntimeError(f"Reasoning API failed for {pokemon['name']}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from reasoning model for {pokemon['name']}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} in reasoning response for {pokemon['name']}: {raw[:200]}")

    return result


# ----------------------------------------
# Step 3 — Public API
# ----------------------------------------

def run(pokemon: dict) -> dict:
    """Analyze Pokémon visual anatomy and save result to outputs/pokemon/{id}.json.

    Two-stage: vision model extracts visual facts from sprite, then reasoning
    model produces structured anatomy JSON for downstream specialists.
    Skips if a valid file already exists (all required keys present).
    Retries up to _MAX_RETRIES times on failure.

    Args:
        pokemon: Dict with keys id, name, types.

    Returns:
        The analysis dict saved to disk.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    out_path = POKEMON_DIR / f"{pokemon['id']}.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip (exists): %s", out_path.name)
            return existing
        logger.warning("regenerating incomplete file: %s", out_path.name)

    logger.info("analyzing: %s (%s)", pokemon["name"], pokemon["id"])

    # Substep 3.1 — Vision: get visual facts from sprite
    last_error = None
    visual_facts = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            visual_facts = _call_vision(pokemon)
            logger.info("vision ok: %s", pokemon["name"])
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("vision attempt %d/%d failed for %s: %s", attempt, _MAX_RETRIES, pokemon["name"], e)
    else:
        raise RuntimeError(f"Vision all {_MAX_RETRIES} attempts failed for {pokemon['name']}: {last_error}")

    # Substep 3.2 — Reasoning: produce structured anatomy using visual facts
    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            analysis = _call_reasoning(pokemon, visual_facts)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning("reasoning attempt %d/%d failed for %s: %s", attempt, _MAX_RETRIES, pokemon["name"], e)
    else:
        raise RuntimeError(f"Reasoning all {_MAX_RETRIES} attempts failed for {pokemon['name']}: {last_error}")

    analysis["pokemon_id"]      = pokemon["id"]
    analysis["pokemon_name"]    = pokemon["name"]
    analysis["original_types"]  = pokemon["types"]
    analysis["visual_facts"]    = visual_facts

    POKEMON_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    logger.info("saved: %s", out_path.name)
    return analysis
