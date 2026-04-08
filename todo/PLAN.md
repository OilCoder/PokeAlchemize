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
| Sprite        | SDXL (stabilityai/stable-diffusion-xl-base-1.0) + sshh12/sdxl-lora-pokemon |
| Fondo         | SDXL + inpainting/outpainting                 |
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
│   ├── 01_morph_agent.py      # LLM genera instrucción de cambios estructurales (Kontext)
│   ├── 02_negative_agent.py   # genera negative_prompt
│   ├── 03_image_generator.py  # FLUX.1-Kontext: sprite → sprite reimaginado
│   ├── 04_pokemon_agent.py    # describe el Pokémon adaptado al tipo (para fondo)
│   ├── 05_biome_agent.py      # describe el hábitat de la combinación
│   ├── 06_scene_conciliador.py # fusiona pokemon_desc + biome_desc → escena
│   ├── 07_style_agent.py      # genera descriptor de estilo desde styles.json
│   ├── 08_style_conciliador.py # fusiona escena + style_desc → prompt fondo
│   ├── 09_background_generator.py # inpainting/outpainting del fondo alrededor del sprite
│   └── batch_runner.py        # orquesta todo secuencialmente
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

### Phase 3 — Sprite Generator
- [x] `pipeline/01_morph_agent.py`: LLM genera instrucción Kontext describiendo cambios estructurales (rasgos físicos, texturas, colores, forma de extremidades) del Pokémon al nuevo tipo (2026-04-08)
- [x] `pipeline/03_image_generator.py`: reescribir como SDXL img2img + sdxl-lora-pokemon, carga modelo una vez, usa sprite original como base (2026-04-08)
- [x] `outputs/prompts/{id}.json`: campos pokemon_id, pokemon_name, original_types, target_type, sprite_path, instruction, negative_prompt, image_path, generated (2026-04-08)
- [ ] Generar los 2,700 sprites reimaginados, skip si ya existe

### Phase 4 — Batch Runner (sprite) (COMPLETED)
- [x] `pipeline/batch_runner.py`: actualizar secuencia a 01→02→03 (2026-04-08)
- [x] Log de progreso con tqdm, skip y errores sin detener el batch (2026-04-08)
- [x] Summary final: total generadas, saltadas, fallidas (2026-04-08)

### Phase 5 — Background Generator
- [ ] `pipeline/09_background_generator.py`: inpainting/outpainting con FLUX.1-dev alrededor del sprite ya generado
- [ ] Usar prompt de fondo generado por 06_scene_conciliador + 08_style_conciliador
- [ ] `pipeline/batch_runner.py`: extender secuencia a 04→05→06→07→08→09

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
