"""
Prompt Conciliator (E3) — assembles specialist outputs into final FLUX prompt.
Reads _pa, _ps, _pe, _na, _ns JSONs for one (Pokémon, type) combination and
assembles a single prompt (CLIP + T5) and a filtered negative_prompt.
Prompt order: style trigger → species+type → E1 anchor_phrases → PA → PE → PS → style closer.
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

# Words that must never appear in the negative prompt — removing them would break sprite aesthetics
_NEGATIVE_BLACKLIST = {"black", "white", "bold", "outline", "outlines", "cel", "shading"}


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
    # Order: style trigger → species+type → identity anchors → transformation → pose → effects → style closer
    # anchor_phrases from E1 go before PA so identity is established before transformation is described.
    subject = f"pkmnstyle, Ken Sugimori style, solo, white background, {target_type} type {pokemon_name}"

    anchor_phrases = pokemon_analysis.get("anchor_phrases", [])

    body    = parts["pa"].get("body_transformation", "")
    pose    = parts["pe"].get("pose_expression", "")
    style   = parts["ps"].get("style_effects", "")
    closing = "Official Pokémon artwork, bold black outlines, clean cel shading. One pokémon only, no text, no watermarks, no signatures."

    subject_full = subject + ", " + ", ".join(anchor_phrases) + "." if anchor_phrases else subject + "."
    prompt_parts = [p for p in [subject_full, body, pose, style, closing] if p]
    prompt = " ".join(prompt_parts)

    # ----
    # Substep 1.2 — Build negative prompt
    # ----
    neg_anatomy = parts["na"].get("negative_anatomy", "")
    neg_style   = parts["ns"].get("negative_style", "")

    # Filter words that would break sprite aesthetics (e.g. "black" removes bold outlines)
    raw_negative = ", ".join(p for p in [neg_anatomy, neg_style] if p)
    filtered_terms = [
        term for term in raw_negative.split(", ")
        if term.strip().lower() not in _NEGATIVE_BLACKLIST
    ]
    negative_prompt = ", ".join(filtered_terms)

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
