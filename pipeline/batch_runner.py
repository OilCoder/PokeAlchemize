"""
Batch Runner — pipeline orchestrator for PokeAIchemize sprite generation.
Phase A: E1 × 150 Pokémon — anatomy analysis (parallel).
Phase B: E2 × 18 types    — type visual vocabulary (sequential).
Phase C: 5 specialists + E3 conciliator × 2700 combos (parallel combos, parallel specialists).
Phase D: image generation  — Z-Image-Turbo (sequential, GPU).
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
    PROMPTS_PARTS_DIR,
    TYPE_VISUAL_DIR,
    TYPES_FILE,
)

_analyst      = importlib.import_module("pipeline.01_pokemon_analyst")
_designer     = importlib.import_module("pipeline.02_type_designer")
_pa           = importlib.import_module("pipeline.03_anatomy_positive")
_ps           = importlib.import_module("pipeline.04_style_positive")
_pe           = importlib.import_module("pipeline.05_pose_expression")
_na           = importlib.import_module("pipeline.06_anatomy_negative")
_ns           = importlib.import_module("pipeline.07_style_negative")
_conciliator  = importlib.import_module("pipeline.08_prompt_conciliator")
_image_gen    = importlib.import_module("pipeline.09_image_generator")

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


def _run_one_combo(pid: str, ttype: str) -> None:
    """Run 5 specialists in parallel then the E3 conciliator for one combo.

    Args:
        pid: Zero-padded Pokémon ID (e.g. '025').
        ttype: Target type name (e.g. 'fire').

    Raises:
        Exception: Re-raises any error from specialists or conciliator.
    """
    specialists = [_pa, _ps, _pe, _na, _ns]
    with ThreadPoolExecutor(max_workers=len(specialists)) as inner:
        futures = [inner.submit(agent.run, pid, ttype) for agent in specialists]
        for f in futures:
            f.result()  # raises immediately on first failure
    _conciliator.run(pid, ttype)


def _run_phase_c(pokemons: list, types: list) -> None:
    """Phase C — specialists + E3: build prompt parts and assemble final prompts (parallel).

    Runs 5 specialists in parallel per combo, then E3 conciliator.
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
        "Phase C — specialists + E3: %d combos — %d workers",
        total, PROMPT_WORKERS,
    )

    with tqdm(total=total, unit="combo", desc="Phase C") as progress:
        with ThreadPoolExecutor(max_workers=PROMPT_WORKERS) as executor:
            futures = {
                executor.submit(_run_one_combo, pid, ttype): (pid, ttype)
                for pid, ttype in pairs
            }
            ok = err = 0
            for future in as_completed(futures):
                pid, ttype = futures[future]
                try:
                    future.result()
                    ok += 1
                except Exception as e:
                    logger.error("Phase C failed %s/%s: %s", pid, ttype, e)
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
    pokemons  = _load_json(POKEMONS_FILE)
    all_types = _load_json(TYPES_FILE)

    if DEV_POKEMON_IDS is not None:
        pokemons = [p for p in pokemons if p["id"] in DEV_POKEMON_IDS]
    elif DEV_POKEMON_LIMIT is not None:
        pokemons = pokemons[:DEV_POKEMON_LIMIT]

    # target_types: types used to generate combos (may be filtered in dev mode)
    # Phase B always generates E2 for ALL types — NS needs original-type E2 vocabularies
    target_types = all_types
    if DEV_TYPE_NAMES is not None:
        target_types = [t for t in all_types if t["name"] in DEV_TYPE_NAMES]
    elif DEV_TYPES_LIMIT is not None:
        target_types = all_types[:DEV_TYPES_LIMIT]

    logger.info("running: %d pokémon × %d target types", len(pokemons), len(target_types))

    # ----
    # Substep 3.2 — DEV_CLEAN: wipe intermediate outputs
    # ----
    if DEV_CLEAN:
        for directory in (POKEMON_DIR, TYPE_VISUAL_DIR, PROMPTS_PARTS_DIR, PROMPTS_DIR, IMAGES_DIR):
            if directory.exists():
                shutil.rmtree(directory)
                logger.info("cleaned %s", directory)

    # ----
    # Substep 3.3 — Execute phases
    # ----
    _run_phase_a(pokemons)
    _run_phase_b(all_types)          # always all 18 — NS needs original-type vocabularies
    _run_phase_c(pokemons, target_types)
    _image_gen.run()


if __name__ == "__main__":
    run()
