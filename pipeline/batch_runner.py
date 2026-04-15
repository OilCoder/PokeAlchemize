"""
Batch Runner — pipeline orchestrator for PokeAIchemize sprite generation.
Phase A: E1 × 150 Pokémon — anatomy analysis (parallel).
Phase B: E2 × 18 types   — type visual vocabulary (sequential).
Phase C: E3 × 2700 combos — SDXL prompt writing (parallel).
Phase D: image generation  — SDXL + ControlNet + LoRA (sequential, GPU).
Resumable: each phase skips existing output files.
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
    DEV_TYPE_NAMES,
    DEV_TYPES_LIMIT,
    IMAGES_DIR,
    POKEMON_DIR,
    POKEMONS_FILE,
    PROMPT_WORKERS,
    PROMPTS_DIR,
    TYPE_VISUAL_DIR,
    TYPES_FILE,
)

_analyst   = importlib.import_module("pipeline.01_pokemon_analyst")
_designer  = importlib.import_module("pipeline.02_type_designer")
_writer    = importlib.import_module("pipeline.03_prompt_writer")
_image_gen = importlib.import_module("pipeline.04_image_generator")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ----------------------------------------
# Step 1 — Data helpers
# ----------------------------------------

def _load_json(path: Path) -> list:
    """Load JSON list from path.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed list.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------
# Step 2 — Phase runners
# ----------------------------------------

def _run_phase_a(pokemons: list) -> None:
    """Phase A — E1: analyze Pokémon visual anatomy (parallel).

    Args:
        pokemons: List of Pokémon dicts filtered by DEV settings.
    """
    logger.info(
        "Phase A — E1 analyst: %d pokémon — %d workers",
        len(pokemons), PROMPT_WORKERS,
    )
    with tqdm(total=len(pokemons), unit="pokémon", desc="E1 analyst") as progress:
        with ThreadPoolExecutor(max_workers=PROMPT_WORKERS) as executor:
            futures = {executor.submit(_analyst.run, p): p for p in pokemons}
            ok = err = 0
            for future in as_completed(futures):
                pokemon = futures[future]
                try:
                    future.result()
                    ok += 1
                except Exception as e:
                    logger.error("E1 failed %s: %s", pokemon["id"], e)
                    err += 1
                progress.update(1)
    logger.info("Phase A done — ok: %d  failed: %d", ok, err)


def _run_phase_b(types: list) -> None:
    """Phase B — E2: define type visual vocabularies (sequential).

    Args:
        types: List of type dicts filtered by DEV settings.
    """
    logger.info("Phase B — E2 designer: %d types", len(types))
    ok = err = 0
    for type_obj in tqdm(types, unit="type", desc="E2 designer"):
        try:
            _designer.run(type_obj)
            ok += 1
        except Exception as e:
            logger.error("E2 failed %s: %s", type_obj["name"], e)
            err += 1
    logger.info("Phase B done — ok: %d  failed: %d", ok, err)


def _run_phase_c(pokemons: list, types: list) -> None:
    """Phase C — E3: write SDXL prompt sets for all (Pokémon, type) combos (parallel).

    Skips combinations where the target type is one of the Pokémon's native types.

    Args:
        pokemons: List of Pokémon dicts.
        types: List of type dicts.
    """
    pairs = [
        (p["id"], t["name"])
        for p in pokemons
        for t in types
        if t["name"] not in p["types"]
    ]
    total = len(pairs)
    logger.info(
        "Phase C — E3 writer: %d combos — %d workers",
        total, PROMPT_WORKERS,
    )

    with tqdm(total=total, unit="combo", desc="E3 writer") as progress:
        with ThreadPoolExecutor(max_workers=PROMPT_WORKERS) as executor:
            futures = {
                executor.submit(_writer.run, pid, ttype): (pid, ttype)
                for pid, ttype in pairs
            }
            ok = err = 0
            for future in as_completed(futures):
                pid, ttype = futures[future]
                try:
                    future.result()
                    ok += 1
                except Exception as e:
                    logger.error("E3 failed %s/%s: %s", pid, ttype, e)
                    err += 1
                progress.update(1)

    logger.info("Phase C done — ok: %d  failed: %d", ok, err)


# ----------------------------------------
# Step 3 — Orchestrator
# ----------------------------------------

def run() -> None:
    """Run full pipeline: Phase A → B → C → D."""

    # ----
    # Substep 3.1 — Load and filter data
    # ----
    pokemons = _load_json(POKEMONS_FILE)
    types    = _load_json(TYPES_FILE)

    if DEV_POKEMON_IDS is not None:
        pokemons = [p for p in pokemons if p["id"] in DEV_POKEMON_IDS]
    elif DEV_POKEMON_LIMIT is not None:
        pokemons = pokemons[:DEV_POKEMON_LIMIT]
    if DEV_TYPE_NAMES is not None:
        types = [t for t in types if t["name"] in DEV_TYPE_NAMES]
    elif DEV_TYPES_LIMIT is not None:
        types = types[:DEV_TYPES_LIMIT]

    logger.info("running: %d pokémon × %d types", len(pokemons), len(types))

    # ----
    # Substep 3.2 — DEV_CLEAN: wipe intermediate outputs
    # ----
    if DEV_CLEAN:
        for directory in (POKEMON_DIR, TYPE_VISUAL_DIR, PROMPTS_DIR, IMAGES_DIR):
            if directory.exists():
                shutil.rmtree(directory)
                logger.info("cleaned %s", directory)

    # ----
    # Substep 3.3 — Execute phases
    # ----
    _run_phase_a(pokemons)
    _run_phase_b(types)
    _run_phase_c(pokemons, types)
    _image_gen.run()


if __name__ == "__main__":
    run()
