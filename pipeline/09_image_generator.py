"""
Image Generator — Z-Image-Turbo sprite renderer.
Reads agent-generated prompt JSONs from outputs/prompts/ and generates
type-transformed Pokémon sprites. Saves outputs/images/{id}_{type}.png.
Called by batch_runner.py (Phase D), or run standalone for dev sets.
"""

import json
import logging
from pathlib import Path

import torch
from diffusers import ZImagePipeline

from config import (
    DEV_POKEMON_IDS,
    DEV_TYPE_NAMES,
    IMAGE_SIZE,
    IMAGE_STEPS,
    IMAGES_DIR,
    PROMPTS_DIR,
    ZIMAGE_GUIDANCE,
    ZIMAGE_MODEL,
)

logger = logging.getLogger(__name__)


# ----------------------------------------
# Step 1 — Pipeline loader
# ----------------------------------------

def _load_pipeline() -> ZImagePipeline:
    """Load Z-Image-Turbo with sequential CPU offload.

    Sequential offload moves each transformer layer individually between CPU
    and GPU, keeping peak VRAM under 16GB on RTX 4080.

    Returns:
        Loaded ZImagePipeline ready for inference.
    """
    logger.info("loading Z-Image-Turbo: %s", ZIMAGE_MODEL)
    pipe = ZImagePipeline.from_pretrained(ZIMAGE_MODEL, torch_dtype=torch.bfloat16)
    pipe.enable_sequential_cpu_offload()
    logger.info(
        "pipeline ready — size=%d steps=%d guidance=%.1f",
        IMAGE_SIZE, IMAGE_STEPS, ZIMAGE_GUIDANCE,
    )
    return pipe


# ----------------------------------------
# Step 2 — Single image generation
# ----------------------------------------

def _generate_one(pipe: ZImagePipeline, prompt_data: dict) -> Path:
    """Generate one type-transformed Pokémon sprite from an agent-generated prompt.

    Args:
        pipe: Loaded ZImagePipeline.
        prompt_data: Dict with pokemon_id, target_type, and prompt fields.

    Returns:
        Path to the saved output image.
    """
    pokemon_id  = prompt_data["pokemon_id"]
    target_type = prompt_data["target_type"]
    out_path    = IMAGES_DIR / f"{pokemon_id}_{target_type}.png"

    if out_path.exists():
        logger.info("skip (exists): %s", out_path.name)
        return out_path

    torch.cuda.empty_cache()

    image = pipe(
        prompt=prompt_data["prompt"],
        height=IMAGE_SIZE,
        width=IMAGE_SIZE,
        num_inference_steps=IMAGE_STEPS,
        guidance_scale=ZIMAGE_GUIDANCE,
    ).images[0]

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    logger.info("saved: %s", out_path.name)
    return out_path


# ----------------------------------------
# Step 4 — Public API
# ----------------------------------------

def run() -> None:
    """Generate type-transformed sprites from outputs/prompts/ to outputs/images/.

    Loads pipeline once, iterates all prompt JSONs filtered by DEV_POKEMON_IDS
    and DEV_TYPE_NAMES, skips existing outputs.
    Logs a summary line: generated / skipped / failed.
    """
    prompt_files = sorted(PROMPTS_DIR.glob("*.json"))
    if not prompt_files:
        logger.warning("no prompt files found in %s — run phases A/B/C first", PROMPTS_DIR)
        return

    # Filter by dev settings if set
    if DEV_POKEMON_IDS or DEV_TYPE_NAMES:
        prompt_files = [
            pf for pf in prompt_files
            if (not DEV_POKEMON_IDS or pf.stem.split("_")[0] in DEV_POKEMON_IDS)
            and (not DEV_TYPE_NAMES or pf.stem.split("_")[1] in DEV_TYPE_NAMES)
        ]

    logger.info("Phase D — image generation: %d prompts", len(prompt_files))
    pipe = _load_pipeline()

    generated = skipped = failed = 0

    for pf in prompt_files:
        try:
            with open(pf, encoding="utf-8") as f:
                prompt_data = json.load(f)

            out_path        = IMAGES_DIR / f"{prompt_data['pokemon_id']}_{prompt_data['target_type']}.png"
            already_existed = out_path.exists()

            _generate_one(pipe, prompt_data)

            if already_existed:
                skipped += 1
            else:
                generated += 1
        except Exception as e:
            logger.error("failed %s: %s", pf.name, e)
            failed += 1

    logger.info(
        "Phase D done — generated: %d  skipped: %d  failed: %d",
        generated, skipped, failed,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
    run()
