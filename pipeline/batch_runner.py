"""
Batch Runner — pipeline orchestrator for sprite generation.
Phase A (prompts): iterates Pokémon × types, calls morph_agent + negative_agent,
  saves outputs/prompts/{id}.json per Pokémon.
Phase B (images): calls image_generator to produce reimagined sprites.
Resumable: skips combinations that already have an instruction saved.
"""

import importlib
import json
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from config import (
    DEV_CLEAN,
    DEV_POKEMON_IDS,
    DEV_POKEMON_LIMIT,
    DEV_TYPES_LIMIT,
    IMAGES_DIR,
    POKEMONS_FILE,
    PROMPT_WORKERS,
    PROMPTS_DIR,
    SPRITES_DIR,
    TYPES_FILE,
)

_morph_agent    = importlib.import_module("pipeline.01_morph_agent")
_negative_agent = importlib.import_module("pipeline.02_negative_agent")
_image_gen      = importlib.import_module("pipeline.03_image_generator")
_pokemon_agent  = importlib.import_module("pipeline.04_pokemon_agent")
_conciliador    = importlib.import_module("pipeline.05_prompt_conciliador")

generate_morph_instruction   = _morph_agent.generate_morph_instruction
generate_negative_prompt     = _negative_agent.generate_negative_prompt
generate_pokemon_description = _pokemon_agent.generate_pokemon_description
consolidate_prompt           = _conciliador.consolidate_prompt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def _load_json(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_prompt_file(pokemon_id: str) -> list:
    path = PROMPTS_DIR / f"{pokemon_id}.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_prompt_file(pokemon_id: str, entries: list) -> None:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROMPTS_DIR / f"{pokemon_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _entry_complete(entries: list, target_type: str) -> bool:
    for entry in entries:
        if entry["target_type"] == target_type and entry.get("instruction"):
            return True
    return False


def _process_type(pokemon: dict, type_obj: dict, existing_entries: list) -> dict | None:
    """Generate instruction + pokemon_desc + negative prompt for one (pokemon, type) combo.

    Returns a prompt entry dict, or None on error.
    """
    target_type = type_obj["name"]

    # ✅ Skip if target type is already one of the Pokémon's original types
    if target_type in pokemon["types"]:
        return None

    # ✅ Skip if already generated
    if _entry_complete(existing_entries, target_type):
        return None

    # ----
    # Step 1 – Call morph_agent, pokemon_agent and negative_agent in parallel
    # ----
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_morph    = pool.submit(generate_morph_instruction, pokemon, target_type, type_obj["morph_traits"])
        f_pokemon  = pool.submit(generate_pokemon_description, pokemon, target_type)
        f_negative = pool.submit(generate_negative_prompt, pokemon, target_type)
        try:
            morph_instruction = f_morph.result()
            pokemon_desc      = f_pokemon.result()
            negative_prompt   = f_negative.result()
        except RuntimeError as e:
            logger.error("failed %s/%s: %s", pokemon["id"], target_type, e)
            return None

    # ----
    # Step 2 – Consolidate morph + pokemon tags into clean SD prompt
    # ----
    try:
        consolidated = consolidate_prompt(pokemon, target_type, morph_instruction, pokemon_desc)
    except RuntimeError as e:
        logger.error("conciliador failed %s/%s: %s", pokemon["id"], target_type, e)
        consolidated = f"{morph_instruction}, {pokemon_desc}"

    instruction = f"solo, 1pokemon, sugimori ken (style), {pokemon['name']}, no humans, pokemon (creature), white background, {consolidated}"

    # ----
    # Step 3 – Build and return entry
    # ----
    return {
        "pokemon_id":      pokemon["id"],
        "pokemon_name":    pokemon["name"],
        "original_types":  pokemon["types"],
        "target_type":     target_type,
        "sprite_path":     str(SPRITES_DIR / f"{pokemon['id']}.png"),
        "morph_instruction": morph_instruction,
        "pokemon_desc":    pokemon_desc,
        "instruction":     instruction,
        "negative_prompt": negative_prompt,
        "image_path":      str(IMAGES_DIR / f"{pokemon['id']}_{target_type}.png"),
        "generated":       False,
    }


def _run_prompt_phase(pokemons: list, types: list) -> None:
    """Phase A — generate and save all prompts."""
    total = len(pokemons) * len(types)
    logger.info("Phase A — prompts: %d pokémon × %d types = %d combos — %d workers",
                len(pokemons), len(types), total, PROMPT_WORKERS)

    with tqdm(total=total, unit="combo", desc="prompts") as progress:
        with ThreadPoolExecutor(max_workers=PROMPT_WORKERS) as executor:
            for pokemon in pokemons:
                existing_entries = _load_prompt_file(pokemon["id"])

                # Substep – submit one task per type ______________________
                futures = {
                    executor.submit(_process_type, pokemon, t, existing_entries): t
                    for t in types
                }

                new_entries = list(existing_entries)
                for future in as_completed(futures):
                    type_obj = futures[future]
                    try:
                        entry = future.result()
                        if entry is not None:
                            new_entries.append(entry)
                        progress.set_description(
                            f"{pokemon['name']} / {type_obj['name']}", refresh=False
                        )
                    except Exception as e:
                        logger.error("task error %s/%s: %s", pokemon["id"], type_obj["name"], e)
                    progress.update(1)

                _save_prompt_file(pokemon["id"], new_entries)
                logger.info("saved %s.json (%d entries)", pokemon["id"], len(new_entries))

    completed = sum(
        1 for p in pokemons
        for e in _load_prompt_file(p["id"])
        if e.get("instruction")
    )
    logger.info("Phase A done. %d / %d prompts ready.", completed, total)


def run() -> None:
    """Run the full sprite generation pipeline: prompts → images."""

    # ----
    # Step 1 – Load and filter data
    # ----
    pokemons = _load_json(POKEMONS_FILE)
    types    = _load_json(TYPES_FILE)

    if DEV_POKEMON_IDS is not None:
        pokemons = [p for p in pokemons if p["id"] in DEV_POKEMON_IDS]
    elif DEV_POKEMON_LIMIT is not None:
        pokemons = pokemons[:DEV_POKEMON_LIMIT]
    if DEV_TYPES_LIMIT is not None:
        types = types[:DEV_TYPES_LIMIT]

    logger.info("running: %d pokémon × %d types", len(pokemons), len(types))

    # ----
    # Step 2 – DEV_CLEAN: wipe outputs before run
    # ----
    if DEV_CLEAN:
        for directory in (PROMPTS_DIR, IMAGES_DIR):
            if directory.exists():
                shutil.rmtree(directory)
                logger.info("cleaned %s", directory)

    # ----
    # Step 3 – Phase A: generate all prompts
    # ----
    _run_prompt_phase(pokemons, types)

    # ----
    # Step 4 – Phase B: generate all sprites
    # ----
    logger.info("Phase B — image generation")
    _image_gen.run()


if __name__ == "__main__":
    run()
