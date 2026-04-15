"""
Image Generator — SDXL + ControlNet Union + pokesprite LoRA sprite renderer.
Loads pipeline once, extracts PIL lineart from original sprites,
generates 1024px type-transformed Pokémon sprites from all prompt JSONs.
Config matches validated debug/dbg_sdxl_controlnet_v2 parameters.
Saves outputs/images/{id}_{type}.png. Called by batch_runner.py (Phase D).
"""

import json
import logging
from pathlib import Path

import torch
from diffusers import (
    ControlNetModel,
    StableDiffusionXLControlNetPipeline,
)
from PIL import Image, ImageFilter, ImageOps

from config import (
    CONTROLNET_MODEL,
    CONTROLNET_SCALE,
    GUIDANCE_SCALE,
    IMAGE_SIZE,
    IMAGE_STEPS,
    IMAGES_DIR,
    LORA_PATH,
    LORA_SCALE,
    PROMPTS_DIR,
    SDXL_MODEL,
    SPRITES_DIR,
)

logger = logging.getLogger(__name__)


# ----------------------------------------
# Step 1 — Pipeline loader
# ----------------------------------------

def _load_pipeline() -> StableDiffusionXLControlNetPipeline:
    """Load SDXL + ControlNet Union + pokesprite LoRA.

    Uses default scheduler (same as validated dbg_sdxl_controlnet_v2).

    Returns:
        Loaded StableDiffusionXLControlNetPipeline ready for inference.
    """
    logger.info("loading ControlNet: %s", CONTROLNET_MODEL)
    controlnet = ControlNetModel.from_pretrained(
        CONTROLNET_MODEL,
        torch_dtype=torch.float16,
        use_safetensors=True,
    )

    logger.info("loading SDXL: %s", SDXL_MODEL)
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        SDXL_MODEL,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    )
    pipe.enable_model_cpu_offload()

    logger.info("loading LoRA: %s (scale=%.2f)", LORA_PATH, LORA_SCALE)
    pipe.load_lora_weights(LORA_PATH)
    pipe.fuse_lora(lora_scale=LORA_SCALE)

    logger.info(
        "pipeline ready — size=%d steps=%d guidance=%.1f controlnet=%.2f lora=%.2f",
        IMAGE_SIZE, IMAGE_STEPS, GUIDANCE_SCALE, CONTROLNET_SCALE, LORA_SCALE,
    )
    return pipe


# ----------------------------------------
# Step 2 — Lineart extraction
# ----------------------------------------

def _load_sprite(pokemon_id: str) -> Image.Image:
    """Load sprite PNG, composite on white background, resize to IMAGE_SIZE.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').

    Returns:
        RGB PIL image resized to IMAGE_SIZE × IMAGE_SIZE.
    """
    sprite_path = SPRITES_DIR / f"{pokemon_id}.png"
    sprite      = Image.open(sprite_path).convert("RGBA")
    bg          = Image.new("RGB", sprite.size, (255, 255, 255))
    bg.paste(sprite, mask=sprite.split()[3])
    return bg.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)


def _extract_lineart(image: Image.Image) -> Image.Image:
    """Extract lineart using GaussianBlur + FIND_EDGES + binary threshold.

    GaussianBlur antes de FIND_EDGES consolida el gradiente en un único pico
    por borde, evitando la línea doble del kernel Laplaciano puro.
    Umbral binario elimina el halo y produce líneas limpias.

    Args:
        image: RGB sprite image at IMAGE_SIZE.

    Returns:
        RGB lineart image (black lines on white background).
    """
    gray   = image.convert("L")
    gray   = gray.filter(ImageFilter.GaussianBlur(radius=1))
    edges  = gray.filter(ImageFilter.FIND_EDGES)
    edges  = edges.point(lambda x: 255 if x > 20 else 0)
    return ImageOps.invert(edges).convert("RGB")


# ----------------------------------------
# Step 3 — Single image generation
# ----------------------------------------

def _generate_one(
    pipe: StableDiffusionXLControlNetPipeline,
    prompt_data: dict,
) -> Path:
    """Generate a type-transformed Pokémon sprite from one prompt JSON.

    Args:
        pipe: Loaded StableDiffusionXLControlNetPipeline.
        prompt_data: Dict with pokemon_id, target_type, prompt, prompt_2,
                     negative, negative_2.

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
    sprite  = _load_sprite(pokemon_id)
    lineart = _extract_lineart(sprite)

    image = pipe(
        prompt=prompt_data["prompt"],
        prompt_2=prompt_data["prompt_2"],
        negative_prompt=prompt_data["negative"],
        negative_prompt_2=prompt_data["negative_2"],
        image=lineart,
        controlnet_conditioning_scale=CONTROLNET_SCALE,
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
# Step 4 — Public API
# ----------------------------------------

def run() -> None:
    """Generate all type-transformed sprites from data/prompts/ to outputs/images/.

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

            out_path       = IMAGES_DIR / f"{prompt_data['pokemon_id']}_{prompt_data['target_type']}.png"
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
