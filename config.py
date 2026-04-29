from pathlib import Path

# ----
# Step 1 – Project paths
# ----
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
DOCS_DIR = ROOT_DIR / "docs"
IMAGES_DIR = DOCS_DIR / "outputs" / "images"

POKEMONS_FILE = DATA_DIR / "pokemons.json"
TYPES_FILE    = DATA_DIR / "types.json"
SPRITES_DIR   = DOCS_DIR / "data" / "sprites"

# E1 outputs: one JSON per Pokémon
POKEMON_DIR = OUTPUTS_DIR / "pokemon"
# E2 outputs: one JSON per type
TYPE_VISUAL_DIR = OUTPUTS_DIR / "types_visual"
# Specialist intermediate outputs: {id}_{type}_{agent}.json (pa/ps/pe/na/ns)
PROMPTS_PARTS_DIR = OUTPUTS_DIR / "prompts_parts"
# E3 conciliator outputs: one JSON per (pokemon, type) combination
PROMPTS_DIR = OUTPUTS_DIR / "prompts"
# E4 combo data: per-combo narrative and game data (species_name, lore, moves, diffs)
COMBO_DATA_DIR = OUTPUTS_DIR / "combo_data"

# ----
# Step 2 – Parallelization
# ----
PROMPT_WORKERS = 2  # concurrent threads for E3 prompt generation (reduced to avoid Ollama timeouts)

# ----
# Step 3 – Development settings
# ----
# DEV_POKEMON_IDS: specific Pokémon IDs to run (overrides DEV_POKEMON_LIMIT when set)
# 50 representative Gen 1 Pokémon — excludes legendary birds (144/145/146) and Eevee family.
# Includes first-stage starters (001/004/007) alongside finals for recognizability.
# Removed redundant pairs (Gastly→Gengar, Hitmonlee only, no Grimer/Horsea/Tauros/Onix/Exeggutor).
# Added Ditto (132), Oddish (043), Growlithe (058), Voltorb (100).
DEV_POKEMON_IDS = [
    "001", "003", "004", "006", "007", "009", "012", "015", "018", "024",
    "025", "028", "031", "034", "035", "039", "043", "045", "050", "052",
    "054", "058", "059", "065", "068", "074", "079", "081", "094", "100",
    "104", "106", "109", "113", "122", "123", "124", "125", "126", "127",
    "129", "130", "131", "132", "137", "142", "143", "147", "149", "150",
]
DEV_POKEMON_LIMIT = None
DEV_TYPES_LIMIT   = None
# DEV_TYPE_NAMES: target types — visually distinct spectrum (6 types)
DEV_TYPE_NAMES = [
    "fire", "water", "ghost", "steel", "electric", "fairy",
]
# SIMILAR_TYPE_EXCLUSIONS: skip combos where target is visually too close to original
# e.g. water→ice both share cold-blue palette; rock→ground both share earthy-stone palette
SIMILAR_TYPE_EXCLUSIONS: dict[str, list[str]] = {
    "water":  ["ice"],
    "ice":    ["water"],
    "rock":   ["ground"],
    "ground": ["rock"],
}
DEV_CLEAN = False  # set True to wipe all generated outputs before run

# ----
# Step 4 – Ollama
# ----
OLLAMA_HOST    = "http://172.19.16.1:11434"
OLLAMA_TIMEOUT = 300  # seconds; qwen3:14b needs ~2-3min on cold load

# Available models (ollama list):
#   "qwen3:30b-a3b"             – MoE 30B, best quality, similar speed due to MoE architecture
#   "qwen3:14b"                 – 14B, good quality/speed balance (default)
#   "qwen2.5:14b-instruct-q6_K" – 14B quantized Q6, very precise instruction following
#   "mistral:latest"            – 7B, fastest, less creative
OLLAMA_MODEL        = "qwen3:30b-a3b"    # MoE 30B, ~3B activos/token — mejor razonamiento que 14B denso
OLLAMA_VISION_MODEL = "qwen2.5vl:7b"    # vision-language model; analiza sprites para E1

# ----
# Step 5 – Z-Image-Turbo (image generation)
# ----
ZIMAGE_MODEL    = "Tongyi-MAI/Z-Image-Turbo"
IMAGE_WIDTH     = 512    # square — correct for character portraits
IMAGE_HEIGHT    = 512    # square — Pokémon fills frame, no landscape cropping
IMAGE_STEPS     = 15     # distilled model; 12 steps is sufficient
ZIMAGE_GUIDANCE = 0.0    # Z-Image is distilled — guidance_scale must be 0.0
