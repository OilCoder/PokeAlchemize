from pathlib import Path

# ----
# Step 1 – Project paths
# ----
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
IMAGES_DIR = OUTPUTS_DIR / "images"

POKEMONS_FILE = DATA_DIR / "pokemons.json"
TYPES_FILE    = DATA_DIR / "types.json"
STYLES_FILE   = DATA_DIR / "styles.json"

# outputs/prompts/{id}.json  — web-facing: final_prompt + image_path per combo
# outputs/pipeline/{id}.json — debug/trace: intermediate agent outputs
PROMPTS_DIR  = OUTPUTS_DIR / "prompts"
PIPELINE_DIR = OUTPUTS_DIR / "pipeline"

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
DEV_TYPES_LIMIT   = 2     # out of 18
DEV_STYLES_LIMIT  = 1     # out of 5 (pixel_art first during dev)
DEV_CLEAN         = True  # delete existing prompts and images before each run

# ----
# Step 4 – Ollama
# ----
OLLAMA_HOST    = "http://172.19.16.1:11434"
OLLAMA_TIMEOUT = 180  # seconds; qwen3:14b needs ~2min on cold load

# Available models (ollama list):
#   "qwen3:30b-a3b"          – MoE 30B, mejor calidad, velocidad similar a 14B por arquitectura MoE
#   "qwen3:14b"              – 14B, buen balance calidad/velocidad (default)
#   "qwen2.5:14b-instruct-q6_K" – 14B cuantizado Q6, muy preciso siguiendo instrucciones
#   "qwen2.5:14b"            – 14B base, similar al anterior
#   "mistral:latest"         – 7B, el más rápido, menos creativo
OLLAMA_MODEL = "qwen3:14b"

# ----
# Step 5 – Image generation
# ----
# Models are assigned per style in data/styles.json.
# All are SDXL-based, fit in 16GB VRAM, and support compel long-prompt encoding.
AVAILABLE_MODELS = {
    "stabilityai/stable-diffusion-xl-base-1.0": "fp16",   # base SDXL, fastest
    "Lykon/dreamshaper-xl-1-0":                 "fp16",   # anime/illustration fine-tune
    "RunDiffusion/Juggernaut-XL-v9":            "fp16",   # photorealistic/dark fantasy fine-tune
}
IMAGE_SIZE  = 768
IMAGE_STEPS = 30
