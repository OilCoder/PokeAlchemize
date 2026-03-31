"""
Batch Runner — pipeline orchestrator for Phase 2 (prompt generation).
Iterates over all Pokémon × types × styles, calls all agents in sequence,
and saves two JSON files per Pokémon:
  - outputs/prompts/{id}.json   → web-facing (final_prompt + metadata)
  - outputs/pipeline/{id}.json  → debug/trace (intermediate agent outputs)
Resumable: skips combinations that already have a final_prompt.
Parallel: types parallelized across pokemons; within each type, scene agents
and style agents also run concurrently.
"""

import importlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from config import (
    DEV_CLEAN,
    DEV_POKEMON_IDS,
    DEV_POKEMON_LIMIT,
    DEV_STYLES_LIMIT,
    DEV_TYPES_LIMIT,
    IMAGES_DIR,
    PIPELINE_DIR,
    POKEMONS_FILE,
    PROMPT_WORKERS,
    PROMPTS_DIR,
    STYLES_FILE,
    TYPES_FILE,
)

_pokemon_agent     = importlib.import_module("pipeline.01_pokemon_agent")
_biome_agent       = importlib.import_module("pipeline.02_biome_agent")
_scene_conciliador = importlib.import_module("pipeline.03_scene_conciliador")
_style_agent       = importlib.import_module("pipeline.04_style_agent")
_style_conciliador = importlib.import_module("pipeline.05_style_conciliador")
_negative_agent    = importlib.import_module("pipeline.06_negative_agent")

generate_pokemon_description = _pokemon_agent.generate_pokemon_description
generate_biome_description   = _biome_agent.generate_biome_description
reconcile_scene              = _scene_conciliador.reconcile_scene
generate_style_prompt        = _style_agent.generate_style_prompt
reconcile_style              = _style_conciliador.reconcile_style
generate_negative_prompt     = _negative_agent.generate_negative_prompt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def _clean_pokemon(pokemon_id: str, styles: list) -> None:
    """Delete existing prompt file and images for a Pokémon before regenerating."""
    prompt_file = PROMPTS_DIR / f"{pokemon_id}.json"
    if prompt_file.exists():
        prompt_file.unlink()

    for image_file in IMAGES_DIR.glob(f"{pokemon_id}_*.png"):
        image_file.unlink()


def _load_json(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(directory: Path, pokemon_id: str, entries: list) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{pokemon_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _load_prompt_file(pokemon_id: str) -> list:
    path = PROMPTS_DIR / f"{pokemon_id}.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def _find_entry(entries: list, target_type: str, style_id: str) -> dict | None:
    for entry in entries:
        if entry["target_type"] == target_type and entry["style_id"] == style_id:
            return entry
    return None


def _entry_complete(entries: list, target_type: str, style_id: str) -> bool:
    entry = _find_entry(entries, target_type, style_id)
    return entry is not None and "negative_prompt" in entry


def _process_style(
    pokemon: dict,
    target_type: str,
    style: dict,
    scene_desc: str,
    negative_prompt: str,
    pokemon_desc: str,
    biome_desc: str,
) -> tuple[dict, dict] | None:
    """Generate prompt for one style. Returns (prompt_entry, pipeline_entry) or None on error."""
    try:
        style_desc   = generate_style_prompt(style)
        final_prompt = reconcile_style(scene_desc, style_desc)
    except RuntimeError as e:
        logger.error("failed %s/%s/%s: %s", pokemon["id"], target_type, style["id"], e)
        return None

    image_filename = f"{pokemon['id']}_{target_type}_{style['id']}.png"
    prompt_entry = {
        "pokemon_id":      pokemon["id"],
        "pokemon_name":    pokemon["name"],
        "original_types":  pokemon["types"],
        "target_type":     target_type,
        "style_id":        style["id"],
        "style_name":      style["name"],
        "model":           style["model"],
        "final_prompt":    final_prompt,
        "negative_prompt": negative_prompt,
        "image_path":      str(IMAGES_DIR / image_filename),
        "generated":       False,
    }
    pipeline_entry = {
        "pokemon_id":   pokemon["id"],
        "target_type":  target_type,
        "style_id":     style["id"],
        "pokemon_desc": pokemon_desc,
        "biome_desc":   biome_desc,
        "scene_desc":   scene_desc,
        "style_desc":   style_desc,
    }
    return prompt_entry, pipeline_entry


def _process_type(
    pokemon: dict,
    target_type: str,
    styles: list,
    existing_entries: list,
) -> tuple[list, list, int]:
    """Generate prompts for all styles of one (pokemon, type) combo.

    Returns (prompt_entries, pipeline_entries, skipped_count).
    """
    # ✅ Filter styles that still need processing (re-run if missing negative_prompt)
    pending_styles = [s for s in styles if not _entry_complete(existing_entries, target_type, s["id"])]
    skipped = len(styles) - len(pending_styles)

    if not pending_styles:
        return [], [], skipped

    # ----
    # Phase 1 – pokemon_desc + biome_desc + negative_prompt in parallel
    # ----
    with ThreadPoolExecutor(max_workers=3) as scene_pool:
        f_pokemon  = scene_pool.submit(generate_pokemon_description, pokemon, target_type)
        f_biome    = scene_pool.submit(generate_biome_description, pokemon, target_type)
        f_negative = scene_pool.submit(generate_negative_prompt, pokemon, target_type)
        try:
            pokemon_desc    = f_pokemon.result()
            biome_desc      = f_biome.result()
            negative_prompt = f_negative.result()
        except RuntimeError as e:
            logger.error("scene failed %s/%s: %s", pokemon["id"], target_type, e)
            return [], [], skipped

    # ----
    # Phase 2 – reconcile scene (depends on both)
    # ----
    try:
        scene_desc = reconcile_scene(pokemon_desc, biome_desc)
    except RuntimeError as e:
        logger.error("scene reconcile failed %s/%s: %s", pokemon["id"], target_type, e)
        return [], [], skipped

    # ----
    # Phase 3 – all styles in parallel
    # ----
    new_prompt_entries   = []
    new_pipeline_entries = []

    with ThreadPoolExecutor(max_workers=len(pending_styles)) as style_pool:
        style_futures = {
            style_pool.submit(
                _process_style, pokemon, target_type, style, scene_desc, negative_prompt, pokemon_desc, biome_desc
            ): style
            for style in pending_styles
        }
        for future in as_completed(style_futures):
            result = future.result()
            if result is not None:
                prompt_entry, pipeline_entry = result
                new_prompt_entries.append(prompt_entry)
                new_pipeline_entries.append(pipeline_entry)

    return new_prompt_entries, new_pipeline_entries, skipped


def run() -> None:
    """Run the full prompt generation pipeline for all Pokémon × types × styles."""

    # ----
    # Step 1 – Load data files
    # ----
    pokemons = _load_json(POKEMONS_FILE)
    types    = _load_json(TYPES_FILE)
    styles   = _load_json(STYLES_FILE)

    if DEV_POKEMON_IDS is not None:
        pokemons = [p for p in pokemons if p["id"] in DEV_POKEMON_IDS]
    elif DEV_POKEMON_LIMIT is not None:
        pokemons = pokemons[:DEV_POKEMON_LIMIT]
    if DEV_TYPES_LIMIT is not None:
        types = types[:DEV_TYPES_LIMIT]
    if DEV_STYLES_LIMIT is not None:
        styles = styles[:DEV_STYLES_LIMIT]

    if DEV_POKEMON_IDS or DEV_POKEMON_LIMIT or DEV_TYPES_LIMIT or DEV_STYLES_LIMIT:
        logger.info("DEV mode: %d pokémon × %d types × %d styles",
                    len(pokemons), len(types), len(styles))

    total = len(pokemons) * len(types) * len(styles)
    logger.info("Total combinations: %d (%d pokémon × %d types × %d styles) — %d workers",
                total, len(pokemons), len(types), len(styles), PROMPT_WORKERS)

    # ----
    # Step 2 – Iterate Pokémon; parallelize types with ThreadPoolExecutor
    # ----
    with tqdm(total=total, unit="combo") as progress:
        with ThreadPoolExecutor(max_workers=PROMPT_WORKERS) as executor:
            for pokemon in pokemons:
                if DEV_CLEAN:
                    _clean_pokemon(pokemon["id"], styles)
                existing_entries = _load_prompt_file(pokemon["id"])

                # Substep 2.1 – Submit one task per type ______________________
                futures = {
                    executor.submit(_process_type, pokemon, t, styles, existing_entries): t
                    for t in types
                }

                prompt_entries   = list(existing_entries)
                pipeline_entries = []

                # Substep 2.2 – Collect results as types complete ______________________
                for future in as_completed(futures):
                    target_type = futures[future]
                    try:
                        new_prompts, new_pipeline, skipped = future.result()
                        prompt_entries.extend(new_prompts)
                        pipeline_entries.extend(new_pipeline)
                        progress.set_description(f"{pokemon['name']} / {target_type}")
                        progress.update(len(styles))
                    except Exception as e:
                        logger.error("task failed %s/%s: %s", pokemon["id"], target_type, e)
                        progress.update(len(styles))

                # Substep 2.3 – Save both files after all types complete ______________________
                _save_json(PROMPTS_DIR, pokemon["id"], prompt_entries)
                if pipeline_entries:
                    _save_json(PIPELINE_DIR, pokemon["id"], pipeline_entries)
                logger.info("saved %s.json (%d entries)", pokemon["id"], len(prompt_entries))

    # ----
    # Step 3 – Summary
    # ----
    completed = sum(
        1 for p in pokemons
        for entry in _load_prompt_file(p["id"])
        if entry.get("final_prompt")
    )
    logger.info("Done. %d / %d prompts generated.", completed, total)


if __name__ == "__main__":
    run()
