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
DEV_POKEMON_LIMIT = 3   # out of 150
DEV_TYPES_LIMIT   = 2   # out of 18
DEV_STYLES_LIMIT  = 2   # out of 5

# ----
# Step 4 – Ollama
# ----
OLLAMA_HOST = "http://172.19.16.1:11434"

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
IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
IMAGE_SIZE  = 768
IMAGE_STEPS = 30
