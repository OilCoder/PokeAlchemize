"""
Image Generator — FLUX.1-dev + WiroAI pokemon LoRA sprite renderer.
Loads pipeline once, generates type-transformed Pokémon sprites from
prompt JSONs. Uses a single prompt processed by both T5-XXL and CLIP.
Saves outputs/images/{id}_{type}.png. Called by batch_runner.py (Phase D).
"""

import json
import logging
from pathlib import Path

import torch
from diffusers import FluxPipeline

from config import (
    FLUX_LORA,
    FLUX_LORA_WEIGHT,
    FLUX_MODEL,
    GUIDANCE_SCALE,
    IMAGE_SIZE,
    IMAGE_STEPS,
    IMAGES_DIR,
    LORA_SCALE,
    PROMPTS_DIR,
)

logger = logging.getLogger(__name__)


# ----------------------------------------
# Step 1 — Pipeline loader
# ----------------------------------------

def _load_pipeline() -> FluxPipeline:
    """Load FLUX.1-dev with WiroAI pokemon LoRA using sequential CPU offload.

    Sequential offload moves each transformer layer individually between CPU
    and GPU, keeping peak VRAM under 16GB on RTX 4080.

    Returns:
        Loaded FluxPipeline ready for inference.
    """
    logger.info("loading FLUX.1-dev: %s", FLUX_MODEL)
    pipe = FluxPipeline.from_pretrained(FLUX_MODEL, torch_dtype=torch.bfloat16)
    pipe.enable_sequential_cpu_offload()

    logger.info("loading LoRA: %s (scale=%.2f)", FLUX_LORA, LORA_SCALE)
    pipe.load_lora_weights(FLUX_LORA, weight_name=FLUX_LORA_WEIGHT)
    pipe.fuse_lora(lora_scale=LORA_SCALE)

    logger.info(
        "pipeline ready — size=%d steps=%d guidance=%.1f lora=%.2f",
        IMAGE_SIZE, IMAGE_STEPS, GUIDANCE_SCALE, LORA_SCALE,
    )
    return pipe


# ----------------------------------------
# Step 2 — Single image generation
# ----------------------------------------

def _generate_one(pipe: FluxPipeline, prompt_data: dict) -> Path:
    """Generate a type-transformed Pokémon sprite from one prompt JSON.

    Uses dual-encoder prompts: clip_prompt goes to CLIP (identity/structure),
    t5_prompt goes to T5-XXL (full transformation detail).

    Args:
        pipe: Loaded FluxPipeline.
        prompt_data: Dict with pokemon_id, target_type, clip_prompt, t5_prompt,
            and negative_prompt.

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
        negative_prompt=prompt_data.get("negative_prompt", ""),
        num_inference_steps=IMAGE_STEPS,
        guidance_scale=GUIDANCE_SCALE,
        width=IMAGE_SIZE,
        height=IMAGE_SIZE,
    ).images[0]

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    logger.info("saved: %s", out_path.name)
    return out_path


# ----------------------------------------
# Step 3 — Public API
# ----------------------------------------

def run() -> None:
    """Generate all type-transformed sprites from outputs/prompts/ to outputs/images/.

    Loads pipeline once, iterates all prompt JSONs, skips existing outputs.
    Logs a summary line: generated / skipped / failed.
    """
    prompt_files = sorted(PROMPTS_DIR.glob("*.json"))
    if not prompt_files:
        logger.warning("no prompt files found in %s — run phases A/B/C first", PROMPTS_DIR)
        return

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
