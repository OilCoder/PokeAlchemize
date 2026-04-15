# PokeAIchemize — Plan

## Goal
Reimaginar los primeros 150 Pokémon cambiando su tipo base. Para cada combinación
Pokémon × Tipo se genera un sprite del Pokémon reimaginado con cambios estructurales
reales (forma, texturas, rasgos físicos) en estilo Ken Sugimori oficial, luego se
completa con un fondo/escenario acorde al tipo. 150 Pokémon × 18 tipos = 2,700 imágenes
generadas localmente (RTX 4080), pre-generadas en batch; la web solo muestra resultados estáticos.

## Stack
| Capa          | Tecnología                                    |
|---------------|-----------------------------------------------|
| LLM (prompts) | Ollama — qwen3:30b-a3b                        |
| Sprite        | FLUX.1-dev (black-forest-labs) + WiroAI/pokemon-flux-lora |
| Fondo         | libre (generado por el modelo)                |
| Datos Pokémon | sprites locales en data/sprites/              |
| Web           | HTML / CSS / JS estático                      |
| Orquestación  | Python puro                                   |
| Aislamiento   | Docker + docker-compose                       |

## Structure
```
PokeAIchemize/
├── data/
│   ├── pokemons.json          # 150 pokémon (id, nombre, tipos, sprite_path)
│   ├── types.json             # 18 tipos oficiales con morph_traits por tipo
│   ├── styles.json            # 5 estilos visuales (usados en fase fondo)
│   └── sprites/               # sprites originales (001.png … 150.png)
├── pipeline/
│   ├── 01_pokemon_analyst.py   # E1: analiza rasgos visuales de cada Pokémon → data/pokemon/{id}.json
│   ├── 02_type_designer.py     # E2: define vocabulario visual de cada tipo → data/types/{type}.json
│   ├── 03_prompt_writer.py     # E3: combina E1+E2 → 4 strings por combinación → data/prompts/{id}_{type}.json
│   ├── 04_image_generator.py   # SDXL+ControlNet+LoRA: lineart+prompt → sprite reimaginado
│   └── batch_runner.py         # orquesta todo secuencialmente
├── outputs/
│   ├── images/                # {id}_{tipo}.png
│   └── prompts/               # {id}.json — instrucciones + metadata por Pokémon
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── config.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Phases

### Phase 1 — Datos (COMPLETED)
- [x] `data/pokemons.json`: 150 Pokémon vía PokéAPI (id, nombre, tipos, sprite_url)
- [x] `data/types.json`: 18 tipos oficiales
- [x] `data/sprites/`: 150 sprites originales descargados localmente

### Phase 2 — Migración del pipeline (COMPLETED)
- [x] `config.py`: actualizar paths, definir modelo FLUX.1-Kontext-dev y LoRA pokemon-flux-lora, eliminar referencias obsoletas (2026-04-08)
- [x] `data/types.json`: agregar campo `morph_traits` por tipo (rasgos físicos típicos: ej. fire → flame tail, ember scales) (2026-04-08)
- [x] Renombrar `pipeline/01_pokemon_agent.py` → `pipeline/04_pokemon_agent.py` (2026-04-08)
- [x] Renombrar `pipeline/02_biome_agent.py` → `pipeline/05_biome_agent.py` (2026-04-08)
- [x] Renombrar `pipeline/03_scene_conciliador.py` → `pipeline/06_scene_conciliador.py` (2026-04-08)
- [x] Renombrar `pipeline/04_style_agent.py` → `pipeline/07_style_agent.py` (2026-04-08)
- [x] Renombrar `pipeline/05_style_conciliador.py` → `pipeline/08_style_conciliador.py` (2026-04-08)
- [x] Renombrar `pipeline/06_negative_agent.py` → `pipeline/02_negative_agent.py` (2026-04-08)
- [x] Renombrar `pipeline/07_image_generator.py` → `pipeline/03_image_generator.py` (2026-04-08)

### Phase 3 — Prompt Generation (3 especialistas)
- [x] `pipeline/01_pokemon_analyst.py`: E1 — Ollama analiza cada Pokémon y extrae identity_traits, original_type_traits, transformable_parts, suppress_colors → `data/pokemon/{id}.json` (150 runs) (2026-04-14)
- [x] `pipeline/02_type_designer.py`: E2 — Ollama define vocabulario visual por tipo: colors, anatomy, effects, suppress_from_others → `data/types_visual/{type}.json` (18 runs) (2026-04-14)
- [x] `pipeline/03_prompt_writer.py`: E3 — Ollama combina E1+E2 y escribe prompt, prompt_2, negative, negative_2 → `data/prompts/{id}_{type}.json` (2700 runs) (2026-04-14)
- [x] `pipeline/01_pokemon_analyst.py`: añadir campo `anchor_phrases` al schema E1 — 2-3 frases exactas para anclar identidad en prompt FLUX (2026-04-15)
- [x] `pipeline/03_prompt_writer.py`: reescribir para FLUX.1-dev — prompt único T5-XXL, patrón "there is no X" para supresión, verbatim anchor_phrases, hard-cap 90 palabras (2026-04-15)

### Phase 4 — Sprite Generator
- [x] `pipeline/04_image_generator.py`: SDXL + ControlNet + pokesprite LoRA, PIL lineart, EulerDiscrete+Karras (2026-04-14)
- [x] `pipeline/batch_runner.py`: orquestar fases A(E1)→B(E2)→C(E3 parallel)→D(imagen), skip si ya existe, summary final (2026-04-14)
- [x] Config baseline v2 validada: IMAGE_SIZE=1024, STEPS=30, GUIDANCE_SCALE=7.5, LORA_SCALE=0.8, CONTROLNET_SCALE=0.4 (2026-04-15)
- [x] Config actual: STEPS=40, GUIDANCE_SCALE=8, LORA_SCALE=0.75, CONTROLNET_SCALE=0.35, EulerDiscrete+Karras (2026-04-15)
- [x] `data/pokemons.json`: Eevee y su familia (133–136) excluidos del dataset (2026-04-15)
- [x] `pipeline/03_prompt_writer.py`: E3 system prompt mejorado — preserva silueta y rasgos icónicos E1, negativos incluyen solo-character enforcement (2026-04-15)
- [x] `pipeline/04_image_generator.py`: migrar SDXL+ControlNet → FLUX.1-dev + FluxPipeline + WiroAI/pokemon-flux-lora (2026-04-15)
- [x] `config.py`: reemplazar parámetros SDXL/ControlNet por FLUX — STEPS=28, GUIDANCE_SCALE=3.5, LORA_SCALE=0.85 (2026-04-15)
- [ ] Validar dev run: 9 Pokémon × 3 tipos = 25 imágenes con FLUX + anchor_phrases + supresión "there is no X"
- [ ] Decidir si escalar a 146 Pokémon × 18 tipos = 2,628 imágenes
- [ ] Generar los ~2,628 sprites reimaginados (batch completo)

### Phase 5 — Experimentos futuros (branch separado)
- [ ] Explorar modelo visual (qwen2.5-vl o llava) como reemplazo de E1 — analizar el sprite
  directamente desde la imagen para extraer rasgos con mayor precisión que el análisis textual
- [ ] Evaluar FLUX.1-schnell como alternativa de velocidad (~30s/imagen vs ~5min con dev)

### Phase 6 — Web Pokédex
- [ ] `web/index.html`: grid de los 150 Pokémon navegable
- [ ] `web/app.js`: al seleccionar un Pokémon, mostrar sprite original + 18 versiones reimaginadas
- [ ] `web/style.css`: diseño estilo Pokédex
- [ ] Nombre del Pokémon y tipo visible en cada tarjeta


## Conventions
- Imágenes: `outputs/images/{id}_{tipo}.png` (ej. `025_fire.png`)
- Prompts: `outputs/prompts/{id}.json` — 18 entradas por archivo
- Instrucciones en inglés (idioma del modelo de imagen)
- Estilo sprite: Ken Sugimori oficial via WiroAI/pokemon-flux-lora
- Sin base de datos: todo en JSON estático
- Sin servidor backend
