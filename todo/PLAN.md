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
| Sprite        | Z-Image-Turbo (Tongyi-MAI/Z-Image-Turbo)                  |
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
│   ├── types.json             # 18 tipos oficiales
│   └── sprites/               # sprites originales (001.png … 150.png)
├── pipeline/
│   ├── 01_pokemon_analyst.py   # E1: analiza rasgos visuales → outputs/pokemon/{id}.json
│   ├── 02_type_designer.py     # E2: vocabulario visual por tipo → outputs/types_visual/{type}.json
│   ├── 03_anatomy_positive.py  # PA: transformación corporal por parte → outputs/prompts_parts/{id}_{type}_pa.json
│   ├── 04_style_positive.py    # PS: efectos visuales y atmósfera → outputs/prompts_parts/{id}_{type}_ps.json
│   ├── 05_pose_expression.py   # PE: pose y expresión → outputs/prompts_parts/{id}_{type}_pe.json
│   ├── 06_anatomy_negative.py  # NA: supresión de rasgos corporales originales → outputs/prompts_parts/{id}_{type}_na.json
│   ├── 07_style_negative.py    # NS: supresión de colores/efectos originales → outputs/prompts_parts/{id}_{type}_ns.json
│   ├── 08_prompt_conciliator.py # E3: ensambla PA+PS+PE+NA+NS → outputs/prompts/{id}_{type}.json
│   ├── 09_image_generator.py   # FLUX.1-dev + LoRA: prompt → sprite reimaginado
│   └── batch_runner.py         # orquesta fases A→B→C(paralelo)→D
├── outputs/
│   ├── images/                # {id}_{tipo}.png
│   ├── prompts/               # {id}_{type}.json — prompt + negative_prompt final
│   ├── prompts_parts/         # {id}_{type}_{pa|ps|pe|na|ns}.json — partes intermedias
│   ├── pokemon/               # {id}.json — análisis E1
│   └── types_visual/          # {type}.json — vocabulario visual E2
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

### Phase 3 — Prompt Generation (3 especialistas) (COMPLETED)
- [x] `pipeline/01_pokemon_analyst.py`: E1 — Ollama analiza cada Pokémon y extrae identity_traits, original_type_traits, transformable_parts, suppress_colors → `outputs/pokemon/{id}.json` (2026-04-14)
- [x] `pipeline/02_type_designer.py`: E2 — Ollama define vocabulario visual por tipo: colors, anatomy, effects, suppress_from_others → `outputs/types_visual/{type}.json` (2026-04-14)
- [x] `pipeline/01_pokemon_analyst.py`: añadir campo `anchor_phrases` al schema E1 (2026-04-15)
- [x] Reemplazar `03_prompt_writer.py` por arquitectura 5 especialistas + conciliador (2026-04-15)
- [x] `pipeline/03_anatomy_positive.py`: PA — transformación de cada parte del cuerpo → `outputs/prompts_parts/{id}_{type}_pa.json` (2026-04-16)
- [x] `pipeline/04_style_positive.py`: PS — efectos visuales, aura, atmósfera → `outputs/prompts_parts/{id}_{type}_ps.json` (2026-04-16)
- [x] `pipeline/05_pose_expression.py`: PE — pose, postura y expresión según personalidad del tipo → `outputs/prompts_parts/{id}_{type}_pe.json` (2026-04-16)
- [x] `pipeline/06_anatomy_negative.py`: NA — lista de rasgos corporales originales a suprimir (2026-04-16)
- [x] `pipeline/07_style_negative.py`: NS — lista de colores/efectos del tipo original a suprimir (2026-04-16)
- [x] `pipeline/08_prompt_conciliator.py`: E3 conciliador — ensambla PA+PS+PE+NA+NS sin LLM → `outputs/prompts/{id}_{type}.json` (2026-04-16)
- [x] `pipeline/batch_runner.py`: rediseñar Phase C — `_run_one_combo` lanza 5 especialistas en paralelo luego E3 (2026-04-16)

### Phase 4 — Sprite Generator
- [x] `pipeline/04_image_generator.py`: SDXL + ControlNet + pokesprite LoRA, PIL lineart, EulerDiscrete+Karras (2026-04-14)
- [x] `pipeline/batch_runner.py`: orquestar fases A(E1)→B(E2)→C(E3 parallel)→D(imagen), skip si ya existe, summary final (2026-04-14)
- [x] Config baseline v2 validada: IMAGE_SIZE=1024, STEPS=30, GUIDANCE_SCALE=7.5, LORA_SCALE=0.8, CONTROLNET_SCALE=0.4 (2026-04-15)
- [x] `data/pokemons.json`: Eevee y su familia (133–136) excluidos del dataset (2026-04-15)
- [x] `pipeline/09_image_generator.py`: migrar SDXL+ControlNet → FLUX.1-dev + FluxPipeline + WiroAI/pokemon-flux-lora + negative_prompt (2026-04-15)
- [x] `config.py`: reemplazar parámetros SDXL/ControlNet por FLUX — STEPS=28, GUIDANCE_SCALE=3.5, LORA_SCALE=0.85 + PROMPTS_PARTS_DIR (2026-04-16)
- [x] Diagnóstico: LoRA sobreimpone colores canónicos cuando el nombre del Pokémon está en el prompt → solución: eliminar nombre del subject (2026-04-16)
- [x] `config.py`: IMAGE_SIZE=768, IMAGE_STEPS=20 validados como config de producción (2026-04-20)
- [x] `pipeline/03_anatomy_positive.py`: agregar campo clip_tags al schema de PA (2026-04-21)
- [x] `pipeline/08_prompt_conciliator.py`: investigar dual-encoder CLIP/T5 — LoRA no tiene pesos CLIP, revertido a prompt único (2026-04-21)
- [x] `pipeline/08_prompt_conciliator.py`: nombre del Pokémon en subject + identity_traits estructurales + negativo suprime colores canónicos (2026-04-21)
- [ ] `pipeline/03_anatomy_positive.py`: corregir system prompt PA — preservar silueta/proporciones explícitamente, solo cambiar materiales/texturas
- [ ] Regenerar todos los prompts del dev set (9 Pokémon × 3 tipos) — prompts actuales tienen formato dual-encoder obsoleto
- [ ] Validar dev run: 9 Pokémon × 3 tipos con arquitectura de prompt actualizada
- [ ] Decidir si escalar a 146 Pokémon × 18 tipos = 2,628 imágenes
- [ ] Generar los ~2,628 sprites reimaginados (batch completo)
- [x] `config.py`: migrar FLUX → Z-Image-Turbo (ZIMAGE_MODEL, IMAGE_SIZE=1024, IMAGE_STEPS=12, ZIMAGE_GUIDANCE=0.0) (2026-04-22)
- [x] `data/types.json`: añadir campos palette, skin_material, accent, seed para los 18 tipos (2026-04-22)
- [x] `pipeline/09_image_generator.py`: migrar FluxPipeline → ZImagePipeline; prompts inline desde types.json + pokemons.json; seed por tipo (2026-04-22)
- [x] Ejecutar set de pruebas Z-Image: 9 Pokémon × 3 tipos = 27 imágenes (`pipeline/09_image_generator.py` standalone) (2026-04-28)
- [x] Evaluar visualmente los 27 resultados — encontrado: dragon=Charizard por "crimson flame tail tip", half-body por resolución landscape 1024×512 (2026-04-28)
- [ ] Decidir si simplificar batch_runner.py para saltar fases A–C con Z-Image (prompts inline no necesitan agentes)
- [ ] Actualizar CLAUDE.md: stack de sprites FLUX → Z-Image-Turbo

### Phase 5 — Mejoras de calidad (COMPLETED)
- [x] `pipeline/01_pokemon_analyst.py`: integrar qwen2.5vl:7b — dos etapas: visión extrae visual_facts del sprite real, qwen3:30b produce JSON de anatomía con hechos visuales como contexto (2026-04-21)
- [x] `pipeline/06_anatomy_negative.py`: corregir prompt NA — suprimir solo estética de tipo (color/material/textura), nunca estructura o silueta del feature (2026-04-21)
- [x] `pipeline/07_style_negative.py`: corregir NS — cargar E2 de tipos ORIGINALES en vez del tipo destino; fix bug que ponía efectos del target type en el negativo (2026-04-21)
- [x] `pipeline/batch_runner.py`: Phase B siempre genera E2 para los 18 tipos independientemente del filtro DEV (2026-04-21)
- [x] Evaluar FLUX.1-schnell como alternativa de velocidad — descartado, calidad inaceptable con 4-12 steps, artefactos anatómicos (2026-04-20)

### Phase 7 — Investigación identidad Pokémon (IP-Adapter)
- [ ] Debug: probar `InstantX/FLUX.1-dev-IP-Adapter` con sprite original como imagen de referencia — preserva identidad via SigLIP sin cambiar pipeline de prompts
- [ ] Evaluar resultado: ¿IP-Adapter preserva silueta + permite transformación de tipo simultánea?
- [ ] Si viable: integrar IP-Adapter en `pipeline/09_image_generator.py` — pasar sprite original como imagen de condicionamiento
- [x] Evaluar Z-Image-Turbo (6B, Apache 2.0, supera FLUX en benchmarks 2026) si IP-Adapter no resuelve identidad — evaluado y elegido como modelo de producción (2026-04-22)

### Phase 6 — Web Pokédex (COMPLETED)
- [x] `web/index.html`: grid de los 150 Pokémon navegable (2026-04-28)
- [x] `web/js/app.js`: sidebar, detalle, filtro por tipo, rightbar con concept/prompt tabs (2026-04-28)
- [x] `web/css/styles.css`: diseño TypeDex estilo Pokédex con dark mode (2026-04-28)
- [x] Nombre del Pokémon y tipo visible en cada tarjeta con SVG icons por tipo (2026-04-28)
- [x] `web/js/type-icons.js`: iconos SVG 16×16 por tipo, `typeIcon()` helper (2026-04-28)
- [x] `web/js/type-system.js`: datos de tipos, colores, conceptos, elementos (2026-04-28)
- [x] `web/js/about.js`: vista "Acerca De" con diagrama interactivo del pipeline (2026-04-28)
- [x] `web/data/bundle.json`: generado por `pipeline/10_bundle_builder.py` (2026-04-28)
- [x] `web/outputs/moves/*.json`: 18 archivos de movimientos temáticos curados por tipo (2026-04-28)
- [x] `web/style-guide.html`: guía de estilos visual del diseño (2026-04-28)


### Phase 8 — Pipeline production run
- [ ] Corregir bug: image generator genera tipos fuera de `DEV_TYPE_NAMES` — investigar si `combo_data` los inyecta ignorando el filtro (`pipeline/09_image_generator.py`)
- [ ] Verificar que Docker tiene el código actual y no una imagen build anterior (`pipeline/batch_runner.py`, `config.py`)
- [ ] Limpiar `outputs/prompts/` y relanzar pipeline con background restaurado y 6 tipos (`pipeline/08_prompt_conciliator.py`)
- [ ] Decidir tratamiento de fondo: transparente con `rembg` vs fondo temático generado por Z-Image
- [ ] Ejecutar run completo: 50 Pokémon × 6 tipos = 300 imágenes (`pipeline/batch_runner.py`)
- [ ] Regenerar `web/data/bundle.json` post-pipeline (`pipeline/10_bundle_builder.py`)
- [ ] Probar web con imágenes reales en `http://localhost:8080/web/`

## Conventions
- Imágenes: `outputs/images/{id}_{tipo}.png` (ej. `025_fire.png`)
- Prompts: `outputs/prompts/{id}.json` — 18 entradas por archivo
- Instrucciones en inglés (idioma del modelo de imagen)
- Estilo sprite: Ken Sugimori oficial via WiroAI/pokemon-flux-lora
- Sin base de datos: todo en JSON estático
- Sin servidor backend
