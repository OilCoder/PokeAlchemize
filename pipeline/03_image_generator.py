"""
Image Generator — sprite reimagining via SD 1.5 txt2img + Ken Sugimori LoRA.
Loads the model once, iterates outputs/prompts/*.json,
generates one sprite per entry from text prompt only.
The Ken Sugimori LoRA is designed to generate Pokémon from text descriptions.
Skips entries where the image already exists (resumable).
"""

import gc
import json
import logging
from pathlib import Path

import torch
from compel import Compel
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from tqdm import tqdm

from config import IMAGE_SIZE, IMAGE_STEPS, PROMPTS_DIR, SPRITE_LORA, SPRITE_MODEL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

BASE_NEGATIVE = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "watermark, text, logo, signature, cropped, out of frame, "
    "realistic, photorealistic, photograph, 3d render, human, person, "
    "multiple views, multiple poses, sprite sheet, collage, side by side, "
    "panel, grid, divided image, two images, tiled, "
    "background, landscape, forest, trees, sky, ground, grass, rocks, "
    "outdoor scene, environment, scenery, grey background, colored background, "
    "gradient background, dark background"
)


def _load_pipeline() -> StableDiffusionPipeline:
    """Load SD 1.5 txt2img pipeline with Ken Sugimori Pokémon LoRA to GPU."""
    logger.info("loading model: %s", SPRITE_MODEL)
    pipe = StableDiffusionPipeline.from_pretrained(
        SPRITE_MODEL,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config, use_karras_sigmas=True
    )
    pipe.to("cuda")
    pipe.load_lora_weights(SPRITE_LORA)
    pipe.vae.enable_tiling()  # fix NaN/black image at 768px
    pipe.set_progress_bar_config(disable=True)
    logger.info("model + LoRA loaded")
    return pipe


def _build_compel(pipe: StableDiffusionPipeline) -> Compel:
    """Build Compel encoder for long-prompt support on SD 1.5."""
    return Compel(
        tokenizer=pipe.tokenizer,
        text_encoder=pipe.text_encoder,
    )


def _generate_sprite(
    pipe: StableDiffusionPipeline,
    compel: Compel,
    instruction: str,
    negative: str,
    image_path: Path,
) -> None:
    """Run txt2img with compel long-prompt encoding and save the sprite to disk."""
    image_path.parent.mkdir(parents=True, exist_ok=True)
    conditioning = compel([instruction, negative])
    image = pipe(
        prompt_embeds=conditioning[0:1],
        negative_prompt_embeds=conditioning[1:2],
        num_inference_steps=IMAGE_STEPS,
        guidance_scale=7.5,
        width=IMAGE_SIZE,
        height=IMAGE_SIZE,
        clip_skip=2,
        cross_attention_kwargs={"scale": 1.0},
    ).images[0]
    image.save(image_path)


def _load_prompt_file(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_prompt_file(path: Path, entries: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def run() -> None:
    """Generate reimagined sprites for all entries in outputs/prompts/."""

    # ----
    # Step 1 – Collect all pending entries
    # ----
    prompt_files = sorted(PROMPTS_DIR.glob("*.json"))
    if not prompt_files:
        logger.warning("no prompt files found in %s", PROMPTS_DIR)
        return

    file_entries: dict[Path, list] = {}
    all_entries: list[tuple[Path, int, dict]] = []

    for file_path in prompt_files:
        entries = _load_prompt_file(file_path)
        file_entries[file_path] = entries
        for idx, entry in enumerate(entries):
            all_entries.append((file_path, idx, entry))

    total   = len(all_entries)
    pending = sum(1 for _, _, e in all_entries if not Path(e["image_path"]).exists())
    logger.info("entries: %d — pending: %d — already done: %d", total, pending, total - pending)

    if pending == 0:
        logger.info("nothing to generate")
        return

    # ----
    # Step 2 – Load model once and generate all sprites
    # ----
    pipe = _load_pipeline()
    compel = _build_compel(pipe)
    generated = skipped = failed = 0
    dirty_files: set[Path] = set()

    with tqdm(total=total, unit="img", desc="sprites") as progress:
        for file_path, idx, entry in all_entries:
            image_path = Path(entry["image_path"])
            progress.set_description(
                f"{entry['pokemon_name']} / {entry['target_type']}",
                refresh=False,
            )

            # ✅ Skip if image already exists
            if image_path.exists():
                skipped += 1
                progress.update(1)
                continue

            # Substep 2.1 – Build full negative prompt ______________________
            entry_negative = entry.get("negative_prompt", "")
            full_negative = f"{BASE_NEGATIVE}, {entry_negative}" if entry_negative else BASE_NEGATIVE

            try:
                # 🎨 Generate reimagined sprite from text prompt
                _generate_sprite(pipe, compel, entry["instruction"], full_negative, image_path)
                file_entries[file_path][idx]["generated"] = True
                dirty_files.add(file_path)
                generated += 1
            except Exception as e:
                logger.error("failed %s: %s", image_path.name, e)
                failed += 1

            progress.update(1)

    # 💾 Save JSON only for files that were updated
    for file_path in dirty_files:
        _save_prompt_file(file_path, file_entries[file_path])

    # 🔄 Free GPU memory
    del pipe
    gc.collect()
    torch.cuda.empty_cache()

    # ----
    # Step 3 – Summary
    # ----
    logger.info("Done. generated: %d | skipped: %d | failed: %d", generated, skipped, failed)


if __name__ == "__main__":
    run()
