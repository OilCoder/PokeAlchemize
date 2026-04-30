"""
Move Illustrator — generates banner images for signature moves.
Reads combo_data for move names/descriptions and types_visual for type vocabulary.
Saves docs/outputs/moves/{id}_{type}_{index}.webp at 384×128.
Called by batch_runner.py as Phase E, after bundle_builder and move_enricher.
"""

import json
import logging
from pathlib import Path

import torch
from diffusers import ZImagePipeline

from config import (
    COMBO_DATA_DIR,
    DOCS_DIR,
    IMAGE_QUALITY,
    IMAGE_STEPS,
    MOVE_EXT,
    MOVE_HEIGHT,
    MOVE_WIDTH,
    TYPE_VISUAL_DIR,
    ZIMAGE_GUIDANCE,
    ZIMAGE_MODEL,
)

logger = logging.getLogger(__name__)

MOVES_DIR = DOCS_DIR / "outputs" / "moves"


# ----------------------------------------
# Step 1 — Prompt builder
# ----------------------------------------

def _extract_visual_keywords(desc: str) -> str:
    """Extract visual nouns from a Spanish move description, stripping action/character words.

    Args:
        desc: Move description in Spanish.

    Returns:
        Comma-separated visual keywords suitable for an image prompt.
    """
    # Words that reference actions, characters or non-visual concepts — strip them
    strip_words = {
        "ataca", "lanza", "cubre", "libera", "absorbe", "paraliza", "paralizan",
        "quema", "queman", "cortar", "corta", "aumenta", "reduce", "usa", "hace",
        "rival", "oponente", "enemigo", "aliado", "usuario", "pokemon",
        "al", "el", "la", "los", "las", "un", "una", "con", "sin", "para",
        "que", "sus", "su", "en", "de", "y", "a", "por", "se", "le", "del",
        "durante", "turno", "turno", "poder", "fuerza", "daño", "movimiento",
    }
    words = desc.replace(",", " ").replace(".", " ").split()
    keywords = [w.lower() for w in words if w.lower() not in strip_words and len(w) > 3]
    return ", ".join(dict.fromkeys(keywords))  # deduplicate, preserve order


def _build_move_prompt(move: dict, type_visual: dict) -> tuple[str, str]:
    """Build a prompt and negative prompt for a move illustration banner.

    Combines move-specific visual keywords with the type's visual vocabulary
    to produce distinct wide-format images per move. No characters or creatures.

    Args:
        move: Dict with 'name' and 'desc' fields from combo_data.
        type_visual: Dict from types_visual/{type}.json with palette, effects, etc.

    Returns:
        Tuple of (prompt, negative_prompt).
    """
    palette      = type_visual.get("palette", "")
    bg           = type_visual.get("background", "")
    type_name    = type_visual.get("type_name", "")
    move_name    = move.get("name", "")
    move_kw      = _extract_visual_keywords(move.get("desc", ""))

    # Filter type effects: drop any referencing a body/creature
    body_words = {"body", "around", "skin", "tail", "limb", "creature", "pokemon"}
    effects    = ", ".join(
        e for e in type_visual.get("effects", [])
        if not any(w in e.lower() for w in body_words)
    )

    prompt = (
        f"{move_name}, {move_kw}, "
        f"pure energy spell effect, {type_name} type attack, "
        f"game VFX concept art, particle burst, elemental explosion, "
        f"{effects}, "
        f"color palette: {palette}, "
        f"background: {bg}, "
        f"wide horizontal banner, cinematic game art, no living beings, "
        f"abstract composition, dramatic lighting"
    )
    negative_prompt = (
        "character, person, humanoid, animal, creature, pokemon, monster, "
        "figure, silhouette, body, face, eyes, hands, feet, wings, tail, "
        "portrait, text, watermark, logo, border, frame, ui element"
    )
    return prompt, negative_prompt


# ----------------------------------------
# Step 2 — Single move image generator
# ----------------------------------------

def _generate_move(pipe: ZImagePipeline, combo_path: Path, type_visual: dict) -> int:
    """Generate banner images for all moves in one combo_data file.

    Args:
        pipe: Loaded ZImagePipeline.
        combo_path: Path to the combo_data JSON file ({id}_{type}.json).
        type_visual: Type visual vocabulary dict.

    Returns:
        Number of images generated (skipped ones not counted).
    """
    with open(combo_path, encoding="utf-8") as f:
        combo = json.load(f)

    moves = combo.get("moves", [])
    if not moves:
        return 0

    stem      = combo_path.stem          # e.g. "001_fire"
    generated = 0

    for idx, move in enumerate(moves[:4]):
        out_path = MOVES_DIR / f"{stem}_{idx}{MOVE_EXT}"
        if out_path.exists():
            logger.info("skip (exists): %s", out_path.name)
            continue

        prompt, negative_prompt = _build_move_prompt(move, type_visual)
        # Prefer Ollama-generated visual_prompt from 12_move_enricher if available
        if move.get("visual_prompt"):
            palette = type_visual.get("palette", "")
            bg      = type_visual.get("background", "")
            prompt  = (
                f"{move['visual_prompt']}, "
                f"pure energy effect, game VFX art, wide horizontal banner, "
                f"color palette: {palette}, background: {bg}, "
                f"no living beings, cinematic game art"
            )

        torch.cuda.empty_cache()
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            height=MOVE_HEIGHT,
            width=MOVE_WIDTH,
            num_inference_steps=IMAGE_STEPS,
            guidance_scale=ZIMAGE_GUIDANCE,
        ).images[0]

        out_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(out_path, quality=IMAGE_QUALITY)
        logger.info("saved: %s", out_path.name)
        generated += 1

    return generated


# ----------------------------------------
# Step 3 — Public API
# ----------------------------------------

def run() -> None:
    """Generate move illustration banners for all combos in combo_data.

    Loads Z-Image-Turbo once, iterates combo_data files filtered to only
    combos with a rendered transformation image (via bundle.json).
    Skips existing outputs. Logs a summary: generated / skipped / failed.
    """
    combo_files = sorted(COMBO_DATA_DIR.glob("*.json"))
    if not combo_files:
        logger.warning("no combo_data files found in %s", COMBO_DATA_DIR)
        return

    # Only generate moves for combos that have a transformation image already rendered.
    # bundle.json transformations maps pokemon_id → [types with images].
    bundle_path = DOCS_DIR / "data" / "bundle.json"
    rendered: set[str] = set()
    if bundle_path.exists():
        with open(bundle_path, encoding="utf-8") as f:
            bundle = json.load(f)
        for pid, types in bundle.get("transformations", {}).items():
            for t in types:
                rendered.add(f"{pid}_{t}")
    combo_files = [cf for cf in combo_files if cf.stem in rendered]

    # Pre-load type visuals
    type_visuals: dict[str, dict] = {}
    for tv_path in TYPE_VISUAL_DIR.glob("*.json"):
        with open(tv_path, encoding="utf-8") as f:
            type_visuals[tv_path.stem] = json.load(f)

    logger.info("Move Illustrator — %d combos to process", len(combo_files))
    pipe = _load_pipeline()

    generated = skipped_files = failed = 0

    for cf in combo_files:
        poke_type = cf.stem.split("_")[1]
        tv = type_visuals.get(poke_type, {})
        try:
            n = _generate_move(pipe, cf, tv)
            generated += n
            if n == 0:
                skipped_files += 1
        except Exception as e:
            logger.error("failed %s: %s", cf.name, e)
            failed += 1

    logger.info(
        "Move Illustrator done — generated: %d  skipped: %d  failed: %d",
        generated, skipped_files, failed,
    )


def _load_pipeline() -> ZImagePipeline:
    """Load Z-Image-Turbo with sequential CPU offload for move generation.

    Returns:
        Loaded ZImagePipeline ready for inference.
    """
    logger.info("loading Z-Image-Turbo: %s", ZIMAGE_MODEL)
    pipe = ZImagePipeline.from_pretrained(ZIMAGE_MODEL, torch_dtype=torch.bfloat16)
    pipe.enable_sequential_cpu_offload()
    logger.info(
        "pipeline ready — %dx%d steps=%d guidance=%.1f",
        MOVE_WIDTH, MOVE_HEIGHT, IMAGE_STEPS, ZIMAGE_GUIDANCE,
    )
    return pipe


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
    run()
