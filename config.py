from pathlib import Path

# ----
# Step 1 – Project paths
# ----
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
IMAGES_DIR = OUTPUTS_DIR / "txt2img"

POKEMONS_FILE = DATA_DIR / "pokemons.json"
TYPES_FILE    = DATA_DIR / "types.json"
SPRITES_DIR   = DATA_DIR / "sprites"

# outputs/prompts/{id}.json — instruction + metadata per combo
PROMPTS_DIR = OUTPUTS_DIR / "prompts"

# ----
# Step 2 – Parallelization
# ----
PROMPT_WORKERS = 6  # concurrent threads for prompt generation (LLM calls)

# ----
# Step 3 – Development settings
# ----
# Limits for development. Set to None to process all.
# DEV_POKEMON_IDS: specific Pokémon IDs to use (overrides DEV_POKEMON_LIMIT when set)
DEV_POKEMON_IDS   = ["001", "004", "007", "025"]  # Bulbasaur, Charmander, Squirtle, Pikachu
DEV_POKEMON_LIMIT = None  # out of 150 (ignored when DEV_POKEMON_IDS is set)
DEV_TYPES_LIMIT   = 3     # normal, fire, water
DEV_CLEAN         = True  # delete existing prompts and images before each run

# ----
# Step 4 – Ollama
# ----
OLLAMA_HOST    = "http://172.19.16.1:11434"
OLLAMA_TIMEOUT = 300  # seconds; qwen3:14b needs ~2-3min on cold load

# Available models (ollama list):
#   "qwen3:30b-a3b"          – MoE 30B, mejor calidad, velocidad similar a 14B por arquitectura MoE
#   "qwen3:14b"              – 14B, buen balance calidad/velocidad (default)
#   "qwen2.5:14b-instruct-q6_K" – 14B cuantizado Q6, muy preciso siguiendo instrucciones
#   "qwen2.5:14b"            – 14B base, similar al anterior
#   "mistral:latest"         – 7B, el más rápido, menos creativo
OLLAMA_MODEL = "qwen3:14b"

# ----
# Step 5 – Sprite image generation (Phase 3)
# ----
SPRITE_MODEL          = "Lykon/AnyLoRA"
SPRITE_LORA           = str(DATA_DIR / "loras" / "pokemon_v3_offset.safetensors")
SPRITE_LORA_FILENAME  = None  # local file, no filename needed
IMAGE_SIZE            = 768   # max recomendado por el LoRA
IMAGE_STEPS           = 50
IMG2IMG_STRENGTH      = 0.999  # 0.0 = sin cambios, 1.0 = ignorar imagen base

# ----
# Step 6 – Background generation (Phase 5 — fondo)
# ----
# STYLES_FILE   = DATA_DIR / "styles.json"
# PIPELINE_DIR  = OUTPUTS_DIR / "pipeline"
# DEV_STYLES_LIMIT = 1
# AVAILABLE_MODELS = {
#     "stabilityai/stable-diffusion-xl-base-1.0": "fp16",
#     "Lykon/dreamshaper-xl-1-0":                 "fp16",
#     "RunDiffusion/Juggernaut-XL-v9":            "fp16",
# }
