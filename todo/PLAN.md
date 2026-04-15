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
| LLM (prompts) | Ollama                                        |
| Sprite        | SDXL (stabilityai/stable-diffusion-xl-base-1.0) + ControlNet (xinsir/controlnet-union-sdxl-1.0) + pokesprite.safetensors LoRA |
| Lineart       | OpenCV Canny nativo (475px) + LANCZOS upscale a 768px |
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
- [ ] `pipeline/01_pokemon_analyst.py`: E1 — Ollama analiza cada Pokémon y extrae identity_traits, original_type_traits, transformable_parts, suppress_colors → `data/pokemon/{id}.json` (150 runs)
- [ ] `pipeline/02_type_designer.py`: E2 — Ollama define vocabulario visual por tipo: colors, anatomy, effects, suppress_from_others → `data/types/{type}.json` (18 runs)
- [ ] `pipeline/03_prompt_writer.py`: E3 — Ollama combina E1+E2 y escribe prompt, prompt_2, negative, negative_2 → `data/prompts/{id}_{type}.json` (2700 runs)

### Phase 4 — Sprite Generator
- [ ] `pipeline/04_image_generator.py`: SDXL + ControlNet (xinsir/controlnet-union-sdxl-1.0) + pokesprite LoRA — lineart Canny+LANCZOS + 4 prompts → sprite 768px
- [ ] Config validada: IMAGE_SIZE=768, STEPS=50, GUIDANCE_SCALE=8.0, LORA_SCALE=0.6, CONTROLNET_SCALE=0.55, EulerDiscrete+Karras
- [ ] `pipeline/batch_runner.py`: orquestar fases 01→02→03→04, skip si ya existe, summary final
- [ ] Generar los 2,700 sprites reimaginados

### Phase 5 — Web Pokédex
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
