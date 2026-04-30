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
- [x] Regenerar todos los prompts del dev set — run completo 50 Pokémon × 6 tipos (2026-04-30)
- [x] Validar dev run: 50 Pokémon × 6 tipos con Z-Image-Turbo (2026-04-30)
- [ ] Decidir si escalar a 146 Pokémon × 18 tipos = 2,628 imágenes
- [ ] Generar los ~2,628 sprites reimaginados (batch completo)
- [x] `config.py`: migrar FLUX → Z-Image-Turbo (ZIMAGE_MODEL, IMAGE_SIZE=1024, IMAGE_STEPS=12, ZIMAGE_GUIDANCE=0.0) (2026-04-22)
- [x] `data/types.json`: añadir campos palette, skin_material, accent, seed para los 18 tipos (2026-04-22)
- [x] `pipeline/09_image_generator.py`: migrar FluxPipeline → ZImagePipeline; prompts inline desde types.json + pokemons.json; seed por tipo (2026-04-22)
- [x] Ejecutar set de pruebas Z-Image: 9 Pokémon × 3 tipos = 27 imágenes (`pipeline/09_image_generator.py` standalone) (2026-04-28)
- [x] Evaluar visualmente los 27 resultados — encontrado: dragon=Charizard por "crimson flame tail tip", half-body por resolución landscape 1024×512 (2026-04-28)
- [x] Decidir si simplificar batch_runner.py — descartado, se mantiene pipeline completo (2026-04-30)
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
- [x] Verificar que Docker tiene el código actual y no una imagen build anterior (`pipeline/batch_runner.py`, `config.py`) (2026-04-29)
- [x] Limpiar `outputs/prompts/` y relanzar pipeline con background restaurado y 6 tipos (`pipeline/08_prompt_conciliator.py`) (2026-04-29)
- [x] Decidir tratamiento de fondo: Z-Image genera fondo temático directamente (2026-04-29)
- [x] Ejecutar run completo: 50 Pokémon × 6 tipos = 278 imágenes (`pipeline/batch_runner.py`) (2026-04-29)
- [x] Regenerar `docs/data/bundle.json` post-pipeline (`pipeline/10_bundle_builder.py`) (2026-04-29)
- [x] Probar web con imágenes reales en `http://localhost:8080/docs/` (2026-04-29)

### Phase 9 — WebP + Move Illustrator (COMPLETED)
- [x] `docs/data/sprites/`: convertir 150 sprites PNG → WebP q=85 (2026-04-29)
- [x] `docs/outputs/images/`: convertir 27 imágenes demo PNG → WebP (2026-04-29)
- [x] `config.py`: agregar constante `IMAGE_EXT = ".webp"` (2026-04-29)
- [x] `pipeline/09_image_generator.py`: guardar como `.webp` quality=85 en lugar de `.png` (2026-04-29)
- [x] `pipeline/10_bundle_builder.py`: escanear `.webp` en lugar de `.png` (2026-04-29)
- [x] `pipeline/11_move_illustrator.py`: nuevo agente — genera imágenes de moves a 384×128 WebP desde `combo_data` + `types_visual` (2026-04-29)
- [x] `docs/js/app.js`: paths `.png` → `.webp`; reemplazar `buildMoveSvg()` por `<img>` con fallback SVG (2026-04-29)
- [x] Regenerar `docs/data/bundle.json` tras cambios de formato (2026-04-29)
- [x] Commit y push: demo con WebP + move images funcionando en GitHub Pages (2026-04-29)

### Phase 10 — Calidad de identidad + Move pipeline
- [x] `config.py`: IMAGE_WIDTH/HEIGHT = 800×800 (2026-04-30)
- [x] `pipeline/13_move_illustrator.py`: renombrar desde 11_ — conflicto con 11_combo_data_writer (2026-04-30)
- [x] `pipeline/batch_runner.py`: Phase E — bundle_builder → move_enricher → move_illustrator (2026-04-30)
- [x] `pipeline/08_prompt_conciliator.py`: soporte array `backgrounds` + composición centrada rotativa (2026-04-30)
- [x] `docs/outputs/types_visual/water.json`: array `backgrounds` con 5 escenarios distintos (2026-04-30)
- [x] `pipeline/01_pokemon_analyst.py`: campo `body_plan` en visión + anchor_phrases mapean body_plan directamente (2026-04-30)
- [x] `pipeline/02_type_designer.py`: campo `anatomy` limitado a superficies — body structure prohibido (2026-04-30)
- [x] Ejecutar run 50 Pokémon × 6 tipos = 278 imágenes + 108 moves — identidad evaluada (2026-04-30)
- [ ] Relanzar pipeline con correcciones E1/E2 de identidad (body_plan + anatomy-neutral)
- [ ] Evaluar identidad post-fix: Gyarados, Magikarp, Porygon, Jynx, tipo steel
- [ ] Actualizar array `backgrounds` en los 17 tipos restantes (solo water tiene variantes actualmente)
- [ ] Actualizar CLAUDE.md: IMAGE_SIZE=800, Phase E moves, sprites en docs/data/sprites/

## Conventions
- Imágenes: `docs/outputs/images/{name}_{type}.webp`
- Moves: `docs/outputs/moves/{id}_{type}_{index}.webp` (384×128)
- Sprites web: `docs/data/sprites/{id}.webp`
- Prompts: `docs/outputs/prompts/{id}_{type}.json`
- Instrucciones en inglés (idioma del modelo de imagen)
- Sin base de datos: todo en JSON estático
- Sin servidor backend
