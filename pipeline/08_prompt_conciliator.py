"""
Prompt Conciliator (E3) — assembles specialist outputs into final FLUX prompt.
Reads _pa, _ps, _pe, _na, _ns JSONs for one (Pokémon, type) combination and
assembles: prompt (single text for both CLIP and T5) + negative_prompt.
Species name anchors morphology via T5 (LoRA has no CLIP weights).
Saves outputs/prompts/{id}_{type}.json.
Called by batch_runner.py (Phase C, after parallel specialists).
"""

import json
import logging

from config import (
    POKEMON_DIR,
    PROMPTS_DIR,
    PROMPTS_PARTS_DIR,
)

logger = logging.getLogger(__name__)

_REQUIRED_KEYS  = {"prompt", "negative_prompt"}
_PART_SUFFIXES  = ("pa", "ps", "pe", "na", "ns")

# Color words that signal species-specific or type-specific aesthetics — exclude from CLIP structural anchors
_COLOR_WORDS = {"red", "white", "color", "colour", "green", "blue", "yellow", "brown", "pink",
                "gold", "silver", "orange", "purple", "black", "gray", "grey", "crimson", "violet"}


# ----------------------------------------
# Step 1 — Prompt assembly (no LLM needed)
# ----------------------------------------

def _assemble(pokemon_analysis: dict, parts: dict, target_type: str) -> dict:
    """Assemble specialist outputs into clip_prompt, t5_prompt, and negative_prompt.

    CLIP encoder (~77 tokens): receives clip_prompt — identity, structure, key type tags.
    T5 encoder (~512 tokens): receives t5_prompt — full transformation detail.

    Args:
        pokemon_analysis: E1 output dict (pokemon_name, anchor_phrases).
        parts: Dict mapping suffix → parsed JSON (pa, ps, pe, na, ns).
        target_type: Target type name (e.g. 'fire').

    Returns:
        Dict with 'clip_prompt', 't5_prompt', and 'negative_prompt' strings.
    """
    pokemon_name = pokemon_analysis.get("pokemon_name", "").lower()

    # ----
    # Substep 1.1 — Build prompt
    # ----
    # Species name as "body shape" anchors morphology through T5 (LoRA has no CLIP weights).
    # Structural identity_traits follow to reinforce silhouette within CLIP's 77-token window.
    # Canonical colors are suppressed by the negative prompt.
    subject = f"pkmnstyle, solo, white background, {target_type} type, {pokemon_name} body shape"

    structural_identity = [
        t for t in pokemon_analysis.get("identity_traits", [])
        if not any(c in t.lower() for c in _COLOR_WORDS)
    ][:3]

    body    = parts["pa"].get("body_transformation", "")
    pose    = parts["pe"].get("pose_expression", "")
    style   = parts["ps"].get("style_effects", "")
    closing = "Clean cel-shaded pokémon illustration style with bold outlines and soft shading. There is only one pokémon. No text, no watermarks, no signatures."

    subject_full = subject + ", " + ", ".join(structural_identity) + "." if structural_identity else subject + "."
    prompt_parts = [p for p in [subject_full, body, pose, style, closing] if p]
    prompt = " ".join(prompt_parts)

    # ----
    # Substep 1.2 — Build negative prompt
    # ----
    neg_anatomy = parts["na"].get("negative_anatomy", "")
    neg_style   = parts["ns"].get("negative_style", "")

    neg_parts = [p for p in [neg_anatomy, neg_style] if p]
    negative_prompt = ", ".join(neg_parts) if neg_parts else ""

    return {"prompt": prompt, "negative_prompt": negative_prompt}


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Assemble specialist outputs into dual-encoder prompt JSON for one (Pokémon, type) combo.

    Reads E1 JSON and the five specialist part JSONs (_pa, _ps, _pe, _na, _ns).
    Assembles clip_prompt, t5_prompt, and negative_prompt without calling Ollama.
    Skips if a valid file already exists.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The result dict saved to disk.

    Raises:
        FileNotFoundError: If E1 or any specialist part JSON is missing.
    """
    out_path = PROMPTS_DIR / f"{pokemon_id}_{target_type}.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip E3 (exists): %s", out_path.name)
            return existing

    # ----
    # Substep 2.1 — Load E1
    # ----
    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")
    with open(e1_path, encoding="utf-8") as f:
        pokemon_analysis = json.load(f)

    # ----
    # Substep 2.2 — Load specialist parts
    # ----
    parts = {}
    for suffix in _PART_SUFFIXES:
        part_path = PROMPTS_PARTS_DIR / f"{pokemon_id}_{target_type}_{suffix}.json"
        if not part_path.exists():
            raise FileNotFoundError(f"Part missing: {part_path}")
        with open(part_path, encoding="utf-8") as f:
            parts[suffix] = json.load(f)

    logger.info("E3 assembling: %s × %s", pokemon_id, target_type)

    # ----
    # Substep 2.3 — Assemble and save
    # ----
    result = _assemble(pokemon_analysis, parts, target_type)
    result["pokemon_id"]  = pokemon_id
    result["target_type"] = target_type

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("E3 saved: %s", out_path.name)
    return result
