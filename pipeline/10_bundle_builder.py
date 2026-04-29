"""
Bundle Builder (E5) — generates web/data/bundle.json for the TypeDex frontend.

Merges pipeline outputs into a single JSON bundle consumed by web/js/app.js:
  - allPokemon:     dict {id: pokemon} from data/pokemons.json
  - types:          list of type objects from data/types.json
  - transformations: dict {id: [type, ...]} from scanning outputs/images/
  - pokemonMeta:    dict {id: E1 analysis} from outputs/pokemon/<id>.json

Called manually after a pipeline run, or added to batch_runner post-phase.
Saves web/data/bundle.json (overwrites previous version).
"""

import json
import logging
from pathlib import Path

from config import (
    DATA_DIR,
    DOCS_DIR,
    IMAGE_EXT,
    IMAGES_DIR,
    OUTPUTS_DIR,
    POKEMON_DIR,
    POKEMONS_FILE,
    ROOT_DIR,
    TYPES_FILE,
)

logger = logging.getLogger(__name__)

BUNDLE_DIR = DOCS_DIR / "data"

# ----------------------------------------
# Step 1 — Data loaders
# ----------------------------------------

def _load_all_pokemon() -> dict:
    """Load pokemons.json and key by id.

    Returns:
        Dict mapping pokemon id string → pokemon record.
    """
    with open(POKEMONS_FILE, encoding="utf-8") as f:
        records = json.load(f)
    return {p["id"]: p for p in records}


def _load_types() -> list:
    """Load types.json as a list.

    Returns:
        List of type definition dicts.
    """
    with open(TYPES_FILE, encoding="utf-8") as f:
        return json.load(f)


def _build_transformations(all_pokemon: dict) -> dict:
    """Scan outputs/images/ to discover which (id, type) pairs have images.

    Handles both legacy {id}_{type}.png and current {name}_{type}.png filenames.
    Uses the all_pokemon dict to resolve names back to ids.

    Args:
        all_pokemon: Dict mapping pokemon id → pokemon record (with 'name' field).

    Returns:
        Dict mapping pokemon id → sorted list of types with generated images.
    """
    name_to_id = {rec["name"]: pid for pid, rec in all_pokemon.items()}
    transforms: dict[str, list[str]] = {}
    if not IMAGES_DIR.exists():
        return transforms
    for png in IMAGES_DIR.glob(f"*{IMAGE_EXT}"):
        # Pattern: {name}_{type}.png (e.g. bulbasaur_fire.png)
        stem = png.stem
        parts = stem.split("_", 1)
        if len(parts) != 2:
            continue
        poke_key, poke_type = parts
        # Resolve name → id; fall back to treating poke_key as id (legacy files)
        poke_id = name_to_id.get(poke_key, poke_key)
        transforms.setdefault(poke_id, []).append(poke_type)
    for k in transforms:
        transforms[k].sort()
    return transforms


def _load_pokemon_meta() -> dict:
    """Load all E1 analysis outputs from outputs/pokemon/.

    Returns:
        Dict mapping pokemon id → E1 analysis dict.
    """
    meta: dict[str, dict] = {}
    if not POKEMON_DIR.exists():
        return meta
    for path in POKEMON_DIR.glob("*.json"):
        poke_id = path.stem
        with open(path, encoding="utf-8") as f:
            meta[poke_id] = json.load(f)
    return meta


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run() -> dict:
    """Build and save web/data/bundle.json from current pipeline outputs.

    Returns:
        The bundle dict written to disk.
    """
    logger.info("E5 building bundle…")

    all_pokemon = _load_all_pokemon()
    bundle = {
        "allPokemon":      all_pokemon,
        "types":           _load_types(),
        "transformations": _build_transformations(all_pokemon),
        "pokemonMeta":     _load_pokemon_meta(),
    }

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BUNDLE_DIR / "bundle.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))

    n_poke   = len(bundle["allPokemon"])
    n_trans  = len(bundle["transformations"])
    n_images = sum(len(v) for v in bundle["transformations"].values())
    n_meta   = len(bundle["pokemonMeta"])
    logger.info(
        "E5 bundle saved: %d pokémon, %d with images (%d combos), %d meta → %s",
        n_poke, n_trans, n_images, n_meta, out_path,
    )
    return bundle


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
