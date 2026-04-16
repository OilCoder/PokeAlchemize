# Pipeline Architecture — PokeAIchemize

Genera sprites de Pokémon reimaginados con tipo transformado. 9 módulos en 4 fases orquestadas por `batch_runner.py`.

## Workflow

```
flowchart TD
    A[pokemons.json / types.json] --> PhaseA
    PhaseA[Phase A — E1 analyst\n01_pokemon_analyst.py\nparalelo × 150] --> E1[(outputs/pokemon/{id}.json)]
    A --> PhaseB
    PhaseB[Phase B — E2 designer\n02_type_designer.py\nsecuencial × 18] --> E2[(outputs/types_visual/{type}.json)]
    E1 --> PhaseC
    E2 --> PhaseC
    PhaseC[Phase C — 5 especialistas + E3\nparalelo por combo\nparalelo interno × 5] --> Parts[(outputs/prompts_parts/)]
    Parts --> E3[08_prompt_conciliator.py]
    E3 --> Prompts[(outputs/prompts/{id}_{type}.json)]
    Prompts --> PhaseD[Phase D — imagen\n09_image_generator.py\nsecuencial GPU]
    PhaseD --> Images[(outputs/images/{id}_{type}.png)]
```

## Phases

### Phase A — E1: Pokémon Analyst (`01_pokemon_analyst.py`)

Analiza visualmente cada Pokémon y extrae su anatomía. Corre en paralelo (`PROMPT_WORKERS` threads).

**Input**: entrada de `pokemons.json` — `{id, name, types}`
**Output**: `outputs/pokemon/{id}.json`

```json
{
  "identity_traits": ["small quadruped", "large bulb on back", ...],
  "original_type_traits": ["green leafy bulb with yellow veins", ...],
  "transformable_parts": ["the bulb on its back", "skin coloration", ...],
  "suppress_colors": ["green", "yellow", ...],
  "anchor_phrases": ["large dark eyes", ...],
  "pokemon_id": "001",
  "pokemon_name": "bulbasaur"
}
```

### Phase B — E2: Type Designer (`02_type_designer.py`)

Define el vocabulario visual de cada tipo. Corre secuencialmente (18 tipos, resultado reutilizado por todos los Pokémon).

**Input**: entrada de `types.json` — `{name, description}`
**Output**: `outputs/types_visual/{type}.json`

```json
{
  "colors": { "primary": [...], "secondary": [...], "avoid": [...] },
  "anatomy": ["obsidian scales", "lava cracks", ...],
  "effects": ["ember particles", "heat haze", ...],
  "suppress_from_others": ["water droplets", "frost crystals", ...]
}
```

### Phase C — 5 Especialistas + E3 Conciliador

Por cada combo `(pokemon_id, target_type)` se ejecutan 5 especialistas **en paralelo** (ThreadPoolExecutor interno), luego el conciliador ensambla el resultado final.

El outer loop corre `PROMPT_WORKERS=6` combos en paralelo simultáneamente.

#### PA — Anatomy Positive (`03_anatomy_positive.py`)

Describe cómo se transforma cada parte del cuerpo. Lee E1 + E2.

- Campo: `body_transformation` — 4-6 frases descriptivas, colores y texturas específicas
- Output: `outputs/prompts_parts/{id}_{type}_pa.json`

#### PS — Style Positive (`04_style_positive.py`)

Describe efectos visuales y atmósfera del tipo. Lee E2.

- Campo: `style_effects` — 2-4 frases sobre partículas, aura, iluminación
- Termina siempre con: "Clean cel-shaded Pokémon illustration style with bold outlines and soft shading."
- Output: `outputs/prompts_parts/{id}_{type}_ps.json`

#### PE — Pose Expression (`05_pose_expression.py`)

Describe pose, postura y expresión facial según la personalidad del tipo. Lee E1.

- Campo: `pose_expression` — 1-2 frases
- Output: `outputs/prompts_parts/{id}_{type}_pe.json`

#### NA — Anatomy Negative (`06_anatomy_negative.py`)

Lista los rasgos corporales del tipo original que deben suprimirse. Lee E1.

- Campo: `negative_anatomy` — lista separada por comas, 5-10 ítems
- Output: `outputs/prompts_parts/{id}_{type}_na.json`

#### NS — Style Negative (`07_style_negative.py`)

Lista los colores y efectos del tipo original a suprimir. Lee E1 + E2.

- Campo: `negative_style` — lista separada por comas, 5-8 ítems
- Output: `outputs/prompts_parts/{id}_{type}_ns.json`

#### E3 — Prompt Conciliator (`08_prompt_conciliator.py`)

Ensambla las 5 partes en un prompt final **sin llamar a Ollama**.

**Estructura del prompt positivo:**
```
pkmnstyle, solo, white background, {target_type} type.
{body_transformation (PA)}
{pose_expression (PE)}
{style_effects (PS)}
There is only one Pokémon. No text, no watermarks, no signatures.
```

**Negative prompt:**
```
{negative_anatomy (NA)}, {negative_style (NS)}
```

> **Nota de diseño**: el nombre del Pokémon se omite intencionalmente del subject. La LoRA `WiroAI/pokemon-flux-lora` tiene memoria canónica fuerte por nombre — nombrarlo sobreimpone los colores originales y anula la transformación. La descripción estructural del PA establece la identidad sin fijar colores.

Output: `outputs/prompts/{id}_{type}.json`

```json
{
  "prompt": "pkmnstyle, solo, white background, fire type. The bulb on its back...",
  "negative_prompt": "green leafy bulb, yellow veins, ...",
  "pokemon_id": "001",
  "target_type": "fire"
}
```

### Phase D — Image Generator (`09_image_generator.py`)

Genera sprites usando FLUX.1-dev + WiroAI pokemon LoRA. Corre secuencialmente en GPU.

**Modelo**: `black-forest-labs/FLUX.1-dev`
**LoRA**: `WiroAI/pokemon-flux-lora` (`pokemon_flux_lora.safetensors`, scale=0.85)
**Config**: `IMAGE_SIZE=1024, IMAGE_STEPS=28, GUIDANCE_SCALE=3.5`
**Offload**: `enable_sequential_cpu_offload()` — mantiene VRAM bajo 16GB (RTX 4080)

TorchInductor compila durante los primeros ~10 steps de la primera imagen (150s→5s convergencia). Las imágenes siguientes arrancan directamente a ~5s/step.

## Paralelización

| Fase | Estrategia | Workers |
|------|-----------|---------|
| A    | ThreadPoolExecutor outer | `PROMPT_WORKERS=6` |
| B    | Secuencial | — |
| C    | ThreadPoolExecutor outer × inner | outer=6, inner=5 por combo |
| D    | Secuencial | GPU single |

## Skip logic

Todos los módulos verifican si el archivo de salida ya existe con las claves requeridas antes de llamar a Ollama. El pipeline es completamente resumable.

## Configuración relevante (`config.py`)

```python
PROMPT_WORKERS    = 6
OLLAMA_MODEL      = "qwen3:30b-a3b"
FLUX_MODEL        = "black-forest-labs/FLUX.1-dev"
FLUX_LORA         = "WiroAI/pokemon-flux-lora"
IMAGE_SIZE        = 1024
IMAGE_STEPS       = 28
GUIDANCE_SCALE    = 3.5
LORA_SCALE        = 0.85
```

Source: `pipeline/` (todos los módulos), `config.py`, `pipeline/batch_runner.py`
