"""
Image Generator — Phase 3.
Loads each SDXL model once, grouped by style, iterates outputs/prompts/*.json,
generates one 768×768 image per entry, skips existing ones.
Uses compel for long-prompt encoding and per-entry negative_prompt from JSON.
"""

import gc
import json
import logging
from collections import defaultdict
from pathlib import Path

import torch
from compel import Compel, ReturnedEmbeddingsType
from diffusers import StableDiffusionXLImg2ImgPipeline
from PIL import Image
from tqdm import tqdm

from config import AVAILABLE_MODELS, IMAGE_SIZE, IMAGE_STEPS, IMG2IMG_STRENGTH, PROMPTS_DIR, SPRITES_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

BASE_NEGATIVE = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "watermark, text, logo, signature, cropped, out of frame, "
    "realistic, photorealistic, photograph, 3d render, 3d cgi, human, person, "
    "sprite sheet, multiple panels, tiled image, 2x2 grid, repeated character, "
    "multiple poses, animation frames, multi-frame, collage, side by side"
)


def _load_pipeline(model_id: str) -> StableDiffusionXLImg2ImgPipeline:
    """Load one SDXL img2img model to GPU."""
    variant = AVAILABLE_MODELS[model_id]
    logger.info("loading model: %s", model_id)
    pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant=variant,
    )
    pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)
    logger.info("model loaded")
    return pipe


def _prepare_reference_image(pokemon_id: str) -> Image.Image:
    """Load official artwork, composite on white background, resize to IMAGE_SIZE."""
    path = SPRITES_DIR / f"{pokemon_id}.png"
    img = Image.open(path).convert("RGBA")

    # Substep – composite transparent PNG on white background ______________________
    background = Image.new("RGBA", img.size, (255, 255, 255, 255))
    background.paste(img, mask=img.split()[3])
    return background.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)


def _build_compel(pipe: StableDiffusionXLImg2ImgPipeline) -> Compel:
    """Build Compel encoder for long-prompt support on SDXL."""
    return Compel(
        tokenizer=[pipe.tokenizer, pipe.tokenizer_2],
        text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
        returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
        requires_pooled=[False, True],
    )


def _generate_image(
    pipe: StableDiffusionXLImg2ImgPipeline,
    compel: Compel,
    prompt: str,
    negative: str,
    reference: Image.Image,
    image_path: Path,
) -> None:
    """Generate one image using reference artwork and save to disk."""
    image_path.parent.mkdir(parents=True, exist_ok=True)
    conditioning, pooled = compel([prompt, negative])
    image = pipe(
        image=reference,
        prompt_embeds=conditioning[0:1],
        pooled_prompt_embeds=pooled[0:1],
        negative_prompt_embeds=conditioning[1:2],
        negative_pooled_prompt_embeds=pooled[1:2],
        num_inference_steps=IMAGE_STEPS,
        strength=IMG2IMG_STRENGTH,
        guidance_scale=7.0,
    ).images[0]
    image.save(image_path)


def _load_prompt_file(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_prompt_file(path: Path, entries: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def run() -> None:
    """Generate images for all entries in outputs/prompts/, grouped by model."""

    # ----
    # Step 1 – Collect all entries and group by model
    # ----
    prompt_files = sorted(PROMPTS_DIR.glob("*.json"))
    if not prompt_files:
        logger.warning("no prompt files found in %s", PROMPTS_DIR)
        return

    file_entries: dict[Path, list] = {}
    groups: dict[str, list] = defaultdict(list)

    total = 0
    for file_path in prompt_files:
        entries = _load_prompt_file(file_path)
        file_entries[file_path] = entries
        for idx, entry in enumerate(entries):
            groups[entry["model"]].append((file_path, idx, entry))
            total += 1

    pending = sum(
        1 for items in groups.values()
        for _, _, e in items
        if not Path(e["image_path"]).exists()
    )
    logger.info("entries: %d — pending: %d — already done: %d", total, pending, total - pending)

    if pending == 0:
        logger.info("nothing to generate")
        return

    # ----
    # Step 2 – Iterate models, load once per model, generate all its images
    # ----
    generated = skipped = failed = 0

    for model_id, items in groups.items():
        pending_for_model = sum(1 for _, _, e in items if not Path(e["image_path"]).exists())
        if pending_for_model == 0:
            logger.info("model %s: all done, skipping", model_id)
            continue

        pipe = _load_pipeline(model_id)
        compel = _build_compel(pipe)
        dirty_files: set[Path] = set()

        with tqdm(total=len(items), unit="img", desc=model_id.split("/")[-1]) as progress:
            for file_path, idx, entry in items:
                image_path = Path(entry["image_path"])
                progress.set_description(
                    f"{entry['pokemon_name']} / {entry['target_type']} / {entry['style_id']}",
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
                    # 🎨 Load reference and generate image
                    reference = _prepare_reference_image(entry["pokemon_id"])
                    _generate_image(pipe, compel, entry["final_prompt"], full_negative, reference, image_path)
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

        # 🔄 Free GPU memory before loading next model
        del pipe, compel
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

    # ----
    # Step 3 – Summary
    # ----
    logger.info("Done. generated: %d | skipped: %d | failed: %d", generated, skipped, failed)


if __name__ == "__main__":
    run()
