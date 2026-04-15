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
SPRITES_DIR   = DATA_DIR / "sprites"

# E1 outputs: one JSON per Pokémon
POKEMON_DIR = DATA_DIR / "pokemon"
# E2 outputs: one JSON per type
TYPE_VISUAL_DIR = DATA_DIR / "types_visual"
# E3 outputs: one JSON per (pokemon, type) combination
PROMPTS_DIR = DATA_DIR / "prompts"

# ----
# Step 2 – Parallelization
# ----
PROMPT_WORKERS = 6  # concurrent threads for E3 prompt generation

# ----
# Step 3 – Development settings
# ----
# DEV_POKEMON_IDS: specific Pokémon IDs to run (overrides DEV_POKEMON_LIMIT when set)
DEV_POKEMON_IDS   = ["001", "004", "007", "025", "039", "052", "054", "094", "143"]
DEV_POKEMON_LIMIT = None
DEV_TYPES_LIMIT   = None
# DEV_TYPE_NAMES: specific type names to run (overrides DEV_TYPES_LIMIT when set)
DEV_TYPE_NAMES    = ["fire", "ice", "ghost"]
DEV_CLEAN         = False  # set True to wipe all generated outputs before run

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
OLLAMA_MODEL = "qwen2.5:14b-instruct-q6_K"

# ----
# Step 5 – SDXL + ControlNet + pokesprite LoRA (image generation)
# ----
SDXL_MODEL       = "stabilityai/stable-diffusion-xl-base-1.0"  # modelo base; entrenado a 1024px nativo
CONTROLNET_MODEL = "xinsir/controlnet-union-sdxl-1.0"          # ControlNet multi-tipo unificado para SDXL
LORA_PATH        = str(DATA_DIR / "loras" / "pokesprite.safetensors")  # LoRA estilo sprite Pokémon; trigger: pkmnstyle
IMAGE_SIZE       = 1024   # resolución nativa SDXL; bajar a 768 degrada la coherencia
IMAGE_STEPS      = 40     # pasos de difusión; 40 con Euler+Karras ≈ calidad de 50 con DDIM
GUIDANCE_SCALE   = 8      # adherencia al prompt; >9 satura colores, <7 pierde el tipo
LORA_SCALE       = 0.75    # peso de la LoRA; 1.0 sobreimpone el estilo, <0.6 lo pierde
CONTROLNET_SCALE = 0.35    # fuerza del lineart; >0.6 rigidiza la pose, <0.3 la ignora
