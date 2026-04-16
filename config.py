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
POKEMON_DIR = OUTPUTS_DIR / "pokemon"
# E2 outputs: one JSON per type
TYPE_VISUAL_DIR = OUTPUTS_DIR / "types_visual"
# Specialist intermediate outputs: {id}_{type}_{agent}.json (pa/ps/pe/na/ns)
PROMPTS_PARTS_DIR = OUTPUTS_DIR / "prompts_parts"
# E3 conciliator outputs: one JSON per (pokemon, type) combination
PROMPTS_DIR = OUTPUTS_DIR / "prompts"

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
OLLAMA_MODEL = "qwen3:30b-a3b"  # MoE 30B, ~3B activos/token — mejor razonamiento que 14B denso

# ----
# Step 5 – FLUX.1-dev + WiroAI pokemon LoRA (image generation)
# ----
FLUX_MODEL        = "black-forest-labs/FLUX.1-dev"          # modelo base; comprensión semántica T5-XXL
FLUX_LORA         = "WiroAI/pokemon-flux-lora"              # LoRA estilo sprite Pokémon; trigger: pkmnstyle
FLUX_LORA_WEIGHT  = "pokemon_flux_lora.safetensors"         # nombre del archivo en el repositorio HF
IMAGE_SIZE        = 1024   # resolución nativa FLUX; óptimo para detalle y coherencia
IMAGE_STEPS       = 28     # FLUX converge en 28 pasos con guidance 3.5
GUIDANCE_SCALE    = 3.5    # rango óptimo FLUX; valores SDXL (7-9) sobreexponen colores
LORA_SCALE        = 0.85   # peso de la LoRA; 1.0 sobreimpone el estilo, <0.6 lo pierde
