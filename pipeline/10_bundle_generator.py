"""
Bundle Generator — builds data/bundle.json for the TypeDex web app.
Reads data/pokemons.json, outputs/pokemon/ (E1 analyses), and outputs/images/
to produce a single JSON bundle consumed by web/js/app.js.

Bundle schema:
  allPokemon    {id: {name, types, id}}              — all 150 Pokémon
  transformations {id: [type, ...]}                  — types with generated images
  pokemonMeta   {id: {pokemon_name, original_types}} — E1 output per Pokémon
Called standalone: python pipeline/10_bundle_generator.py
"""

import json
import logging
from pathlib import Path

from config import DATA_DIR, IMAGES_DIR, POKEMON_DIR, POKEMONS_FILE

logger = logging.getLogger(__name__)

BUNDLE_PATH = DATA_DIR / "bundle.json"


def build() -> dict:
    """Build the web bundle from pipeline outputs and source data.

    Returns:
        Bundle dict with allPokemon, transformations, and pokemonMeta.
    """
    # ----
    # Substep 1 — allPokemon from data/pokemons.json
    # ----
    with open(POKEMONS_FILE, encoding="utf-8") as f:
        pokemons = json.load(f)

    all_pokemon = {
        p["id"]: {"name": p["name"], "types": p["types"], "id": p["id"]}
        for p in pokemons
    }

    # ----
    # Substep 2 — transformations from outputs/images/ filenames
    # ----
    transformations: dict[str, list[str]] = {}
    for img in sorted(IMAGES_DIR.glob("*.png")):
        parts = img.stem.split("_", 1)
        if len(parts) != 2:
            continue
        pid, ttype = parts
        transformations.setdefault(pid, [])
        if ttype not in transformations[pid]:
            transformations[pid].append(ttype)

    # ----
    # Substep 3 — pokemonMeta from outputs/pokemon/{id}.json (E1 outputs)
    # ----
    pokemon_meta: dict[str, dict] = {}
    for e1_file in sorted(POKEMON_DIR.glob("*.json")):
        pid = e1_file.stem
        with open(e1_file, encoding="utf-8") as f:
            data = json.load(f)
        pokemon_meta[pid] = {
            "pokemon_name":   data.get("pokemon_name", ""),
            "original_types": data.get("original_types", []),
        }

    bundle = {
        "allPokemon":    all_pokemon,
        "transformations": transformations,
        "pokemonMeta":   pokemon_meta,
    }

    with open(BUNDLE_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))

    total_images = sum(len(v) for v in transformations.values())
    logger.info(
        "bundle saved: %d pokémon | %d with images | %d total transformations → %s",
        len(all_pokemon), len(transformations), total_images, BUNDLE_PATH,
    )
    return bundle


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    build()
