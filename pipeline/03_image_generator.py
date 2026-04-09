"""
Image Generator — sprite reimagining via FLUX.1-dev txt2img + WiroAI Pokémon LoRA.
Loads the model once with CPU offload for 16GB VRAM compatibility,
iterates outputs/prompts/*.json and generates one sprite per entry.
Trigger word: pkmnstyle. No negative prompt (FLUX does not use CFG negation).
Skips entries where the image already exists (resumable).
"""

import gc
import json
import logging
from pathlib import Path

import torch
from diffusers import FluxPipeline
from tqdm import tqdm

from config import FLUX_GUIDANCE_SCALE, IMAGE_SIZE, IMAGE_STEPS, PROMPTS_DIR, SPRITE_LORA, SPRITE_LORA_FILENAME, SPRITE_MODEL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def _load_pipeline() -> FluxPipeline:
    """Load FLUX.1-dev pipeline with WiroAI Pokémon LoRA, offloaded to fit 16GB VRAM."""
    logger.info("loading model: %s", SPRITE_MODEL)
    pipe = FluxPipeline.from_pretrained(
        SPRITE_MODEL,
        torch_dtype=torch.bfloat16,
    )
    pipe.enable_model_cpu_offload()
    pipe.load_lora_weights(SPRITE_LORA, weight_name=SPRITE_LORA_FILENAME)
    pipe.set_progress_bar_config(disable=True)
    logger.info("model + LoRA loaded")
    return pipe


def _generate_sprite(
    pipe: FluxPipeline,
    instruction: str,
    image_path: Path,
) -> None:
    """Run FLUX txt2img and save the sprite to disk.

    Args:
        pipe: Loaded FLUX pipeline.
        instruction: Positive prompt string (must include pkmnstyle trigger).
        image_path: Output path for the generated image.
    """
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image = pipe(
        prompt=instruction,
        num_inference_steps=IMAGE_STEPS,
        guidance_scale=FLUX_GUIDANCE_SCALE,
        width=IMAGE_SIZE,
        height=IMAGE_SIZE,
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

            try:
                # 🎨 Generate reimagined sprite from text prompt
                _generate_sprite(pipe, entry["instruction"], image_path)
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
