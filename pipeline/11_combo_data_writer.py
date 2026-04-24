"""
Combo Data Writer (E4) — per-combo narrative and game data specialist.
Generates species_name, lore, moves[4], and diffs[4] for each (Pokémon, type) combo.
Saves to outputs/combo_data/{id}_{type}.json.
Called by batch_runner.py (Phase C, after E3 conciliator).
"""

import json
import logging

import requests

from config import COMBO_DATA_DIR, OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, POKEMON_DIR

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"species_name", "lore", "moves", "diffs"}
_MAX_RETRIES   = 3

SYSTEM_PROMPT = """Eres un escritor de lore de Pokémon en español, especializado en transformaciones de tipo elemental.
Dado un Pokémon y su tipo de transformación, genera contenido narrativo y de juego específico para esa combinación.

Devuelve ÚNICAMENTE JSON válido con exactamente estas claves:
{
  "species_name": "nombre de especie transformada en español — 2 o 3 palabras, ej: 'Pokémon Llama Marina'",
  "lore": "descripción narrativa (40-50 palabras en español) específica para ESTE Pokémon con ESTE tipo — menciona su nombre, sus rasgos físicos clave y cómo el nuevo tipo los altera",
  "moves": [
    {"name": "Nombre del Movimiento", "desc": "descripción del movimiento (15-25 palabras)"},
    {"name": "Nombre del Movimiento", "desc": "descripción del movimiento (15-25 palabras)"},
    {"name": "Nombre del Movimiento", "desc": "descripción del movimiento (15-25 palabras)"},
    {"name": "Nombre del Movimiento", "desc": "descripción del movimiento (15-25 palabras)"}
  ],
  "diffs": [
    {"from": "rasgo original del Pokémon", "to": "cómo cambió con el nuevo tipo"},
    {"from": "rasgo original del Pokémon", "to": "cómo cambió con el nuevo tipo"},
    {"from": "rasgo original del Pokémon", "to": "cómo cambió con el nuevo tipo"},
    {"from": "rasgo original del Pokémon", "to": "cómo cambió con el nuevo tipo"}
  ]
}

Reglas:
- species_name: siempre empieza con "Pokémon", luego 1-2 adjetivos o sustantivos combinando identidad + tipo nuevo.
- lore: narrativo, tiempo presente, descriptivo. Specific to this Pokémon — no genérico.
- moves: 4 movimientos únicos combinando la identidad del Pokémon con el nuevo tipo. Nombres creativos en español.
- diffs: 4 filas de transformación. "from" = rasgo concreto del Pokémon original, "to" = cómo cambió con el nuevo tipo. Visual y concreto.
No incluyas explicaciones fuera del JSON."""


# ----------------------------------------
# Step 1 — Ollama call
# ----------------------------------------

def _call_ollama(
    pokemon_name: str,
    original_types: list[str],
    target_type: str,
    anchor: str,
) -> dict:
    """Call Ollama to generate per-combo narrative and game data.

    Args:
        pokemon_name: Pokémon name (e.g. 'Charizard').
        original_types: List of original type names (e.g. ['fire', 'flying']).
        target_type: Target transformation type (e.g. 'water').
        anchor: Top anchor phrase from E1 for identity grounding.

    Returns:
        Parsed JSON dict with species_name, lore, moves, diffs.

    Raises:
        RuntimeError: If Ollama call fails, returns invalid JSON,
                      response is missing required keys, or moves/diffs count < 4.
    """
    orig_str = " / ".join(original_types)
    user_prompt = (
        f"/no_think\n"
        f"Pokémon: {pokemon_name}\n"
        f"Tipos originales: {orig_str}\n"
        f"Tipo de transformación: {target_type}\n"
        f"Rasgos físicos clave: {anchor}\n"
        f"Genera el contenido narrativo y de juego para esta combinación."
    )

    payload = {
        "model":  OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "format": "json",
        "stream": False,
        "think":  False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama request failed for {pokemon_name}/{target_type}: {e}") from e

    raw = resp.json().get("response", "")
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON for {pokemon_name}/{target_type}: {e}") from e

    missing = _REQUIRED_KEYS - result.keys()
    if missing:
        raise RuntimeError(f"Missing keys {missing} for {pokemon_name}/{target_type}: {raw[:200]}")

    if not isinstance(result.get("moves"), list) or len(result["moves"]) < 4:
        raise RuntimeError(f"moves must have 4 items for {pokemon_name}/{target_type}")

    if not isinstance(result.get("diffs"), list) or len(result["diffs"]) < 4:
        raise RuntimeError(f"diffs must have 4 items for {pokemon_name}/{target_type}")

    return result


# ----------------------------------------
# Step 2 — Public API
# ----------------------------------------

def run(pokemon_id: str, target_type: str) -> dict:
    """Generate combo narrative and game data for one (Pokémon, type) combination.

    Skips if a valid output file already exists (all required keys present).
    Retries up to _MAX_RETRIES times on failures.

    Args:
        pokemon_id: Zero-padded Pokémon ID (e.g. '025').
        target_type: Target type name (e.g. 'fire').

    Returns:
        The combo data dict saved to disk.

    Raises:
        FileNotFoundError: If E1 JSON for pokemon_id does not exist.
        RuntimeError: If all retry attempts fail.
    """
    out_path = COMBO_DATA_DIR / f"{pokemon_id}_{target_type}.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        if _REQUIRED_KEYS.issubset(existing.keys()):
            logger.info("skip E4 (exists): %s", out_path.name)
            return existing
        logger.warning("regenerating incomplete E4 file: %s", out_path.name)

    # ----
    # Substep 2.1 — Load E1
    # ----
    e1_path = POKEMON_DIR / f"{pokemon_id}.json"
    if not e1_path.exists():
        raise FileNotFoundError(f"E1 missing: {e1_path}")
    with open(e1_path, encoding="utf-8") as f:
        e1 = json.load(f)

    pokemon_name   = e1.get("pokemon_name", pokemon_id).capitalize()
    original_types = e1.get("original_types", [])
    anchors        = e1.get("anchor_phrases", [])
    top_anchor     = anchors[0] if anchors else ""

    logger.info("E4 writing: %s × %s", pokemon_id, target_type)

    # ----
    # Substep 2.2 — Call LLM with retries
    # ----
    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            data = _call_ollama(pokemon_name, original_types, target_type, top_anchor)
            break
        except RuntimeError as e:
            last_error = e
            logger.warning(
                "attempt %d/%d failed for %s/%s: %s",
                attempt, _MAX_RETRIES, pokemon_id, target_type, e,
            )
    else:
        raise RuntimeError(
            f"All {_MAX_RETRIES} attempts failed for {pokemon_id}/{target_type}: {last_error}"
        )

    # ----
    # Substep 2.3 — Save
    # ----
    data["pokemon_id"]  = pokemon_id
    data["target_type"] = target_type

    COMBO_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("E4 saved: %s", out_path.name)
    return data
