"""
Image Generator — Z-Image-Turbo sprite renderer.
Builds palette-first prompts from types.json + pokemons.json and generates
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
    POKEMONS_FILE,
    TYPES_FILE,
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
# Step 2 — Data loader
# ----------------------------------------

def _load_data() -> tuple[dict, dict]:
    """Load pokemons.json and types.json indexed by key.

    Returns:
        Tuple of (pokemon_by_id, type_by_name) dicts.
    """
    with open(POKEMONS_FILE, encoding="utf-8") as f:
        pokemons = {p["id"]: p for p in json.load(f)}
    with open(TYPES_FILE, encoding="utf-8") as f:
        types = {t["name"]: t for t in json.load(f)}
    return pokemons, types


# ----------------------------------------
# Step 3 — Prompt builder
# ----------------------------------------

def _build_prompt(pokemon: dict, type_data: dict) -> str:
    """Build a palette-first Z-Image prompt from pokemon and type data.

    Palette must come first (~50 tokens) to override Z-Image's canonical
    color priors before attention decays past the effective range.

    Args:
        pokemon: Dict with id, name, types fields.
        type_data: Dict with name, palette, skin_material, accent fields.

    Returns:
        Complete prompt string ready for ZImagePipeline.
    """
    name      = pokemon["name"].capitalize()
    type_name = type_data["name"]
    palette   = type_data["palette"]
    skin      = type_data["skin_material"]
    accent    = type_data["accent"]

    return (
        f"Color palette: {palette}. "
        f"{name} {type_name} type. Ken Sugimori style, cel-shaded, bold black outlines, white background. "
        f"{skin}. "
        f"{accent}. White background, no text."
    )


# ----------------------------------------
# Step 4 — Single image generation
# ----------------------------------------

def _generate_one(
    pipe: ZImagePipeline,
    pokemon: dict,
    type_data: dict,
) -> Path:
    """Generate one type-transformed Pokémon sprite.

    Args:
        pipe: Loaded ZImagePipeline.
        pokemon: Dict with id and name fields.
        type_data: Dict with name, palette, skin_material, accent, seed fields.

    Returns:
        Path to the saved output image.
    """
    pokemon_id = pokemon["id"]
    type_name  = type_data["name"]
    out_path   = IMAGES_DIR / f"{pokemon_id}_{type_name}.png"

    if out_path.exists():
        logger.info("skip (exists): %s", out_path.name)
        return out_path

    prompt    = _build_prompt(pokemon, type_data)
    seed      = type_data.get("seed", 7)
    generator = torch.Generator(device="cpu").manual_seed(seed)

    torch.cuda.empty_cache()
    image = pipe(
        prompt=prompt,
        height=IMAGE_SIZE,
        width=IMAGE_SIZE,
        num_inference_steps=IMAGE_STEPS,
        guidance_scale=ZIMAGE_GUIDANCE,
        generator=generator,
    ).images[0]

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    logger.info("saved: %s", out_path.name)
    return out_path


# ----------------------------------------
# Step 5 — Public API
# ----------------------------------------

def run(
    pokemon_ids: list[str] | None = None,
    type_names: list[str] | None = None,
) -> None:
    """Generate type-transformed sprites for the specified Pokémon and types.

    Loads pipeline once, iterates all (pokemon, type) combinations, skips
    existing outputs. Logs a summary line: generated / skipped / failed.

    Args:
        pokemon_ids: Zero-padded IDs to process. Defaults to DEV_POKEMON_IDS.
        type_names: Type names to process. Defaults to DEV_TYPE_NAMES.
    """
    ids   = pokemon_ids or DEV_POKEMON_IDS
    types = type_names  or DEV_TYPE_NAMES

    pokemons, type_map = _load_data()

    missing_ids   = [i for i in ids   if i not in pokemons]
    missing_types = [t for t in types if t not in type_map]
    if missing_ids:
        logger.warning("unknown pokemon IDs: %s", missing_ids)
    if missing_types:
        logger.warning("unknown types: %s", missing_types)

    combos = [
        (pokemons[i], type_map[t])
        for i in ids   if i in pokemons
        for t in types if t in type_map
    ]
    logger.info("Phase D — image generation: %d combinations", len(combos))
    pipe = _load_pipeline()

    generated = skipped = failed = 0

    for pokemon, type_data in combos:
        try:
            out_path        = IMAGES_DIR / f"{pokemon['id']}_{type_data['name']}.png"
            already_existed = out_path.exists()
            _generate_one(pipe, pokemon, type_data)
            if already_existed:
                skipped += 1
            else:
                generated += 1
        except Exception as e:
            logger.error("failed %s/%s: %s", pokemon["id"], type_data["name"], e)
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
