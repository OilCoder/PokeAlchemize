# PokeAIchemize

Reimagina los 150 Pokémon de Gen 1 cambiando su tipo base usando LLMs locales y generación de imágenes con GPU. Genera hasta 2 700 sprites (150 Pokémon × 18 tipos) y los muestra en una Pokédex web estática.

---

## Estructura del proyecto

```
PokeAIchemize/
│
├── config.py                  # Paths, modelos, parámetros globales (OLLAMA, Z-Image, dev flags)
├── Dockerfile                 # Imagen Docker: PyTorch 2.7 + CUDA 12.6 + dependencias
├── docker-compose.yml         # Servicio pipeline con GPU, volumes montados al host
├── requirements.txt           # Dependencias Python del pipeline
│
├── data/                      # Datos fuente (commitados, inmutables)
│   ├── pokemons.json          # Lista de 150 Pokémon con id, nombre y tipos originales
│   ├── types.json             # 18 tipos con morph_traits para E2
│   ├── styles.json            # Estilos visuales de referencia (legado)
│   ├── sprites/               # Sprites originales 001.png … 150.png
│   └── loras/                 # LoRA weights para Z-Image (pokesprite, pokemon_v3)
│
├── pipeline/                  # Agentes del pipeline (ejecutados dentro de Docker)
│   ├── batch_runner.py        # Orquestador: fases A → B → C → D en orden
│   ├── 01_pokemon_analyst.py  # E1: analiza sprite → identity_traits, anchor_phrases
│   ├── 02_type_designer.py    # E2: diseña vocabulario visual por tipo → palette, skin, accent, background
│   ├── 03_anatomy_positive.py # C-PA: rasgos anatómicos positivos del tipo
│   ├── 04_style_positive.py   # C-PS: rasgos de estilo positivos
│   ├── 05_pose_expression.py  # C-PE: pose y expresión facial
│   ├── 06_anatomy_negative.py # C-NA: rasgos a suprimir (tipo original)
│   ├── 07_style_negative.py   # C-NS: estilos a evitar
│   ├── 08_prompt_conciliator.py # E3: ensambla partes → prompt final Z-Image (77 tokens CLIP)
│   ├── 09_image_generator.py  # Fase D: genera imagen PNG con Z-Image-Turbo (GPU)
│   ├── 10_bundle_builder.py   # E5: genera web/data/bundle.json para la web
│   ├── 11_combo_data_writer.py # E4: escribe combo_data (lore, movimientos, diffs) por combo
│   └── __init__.py
│
├── outputs/                   # Salidas generadas (gitignored, creadas por el pipeline)
│   ├── pokemon/               # E1: {id}.json — análisis anatómico por Pokémon
│   ├── types_visual/          # E2: {type}.json — vocabulario visual por tipo
│   ├── prompts_parts/         # C: {id}_{type}_{pa|ps|pe|na|ns}.json — partes por especialista
│   ├── prompts/               # E3: {id}_{type}.json — prompt ensamblado final
│   ├── combo_data/            # E4: {id}_{type}.json — lore, movimientos, diffs narrativos
│   ├── images/                # D: {id}_{type}.png — sprites generados (512×512)
│   └── run.log                # Log de la última ejecución del pipeline
│
├── web/                       # Frontend estático (servido desde la raíz del proyecto)
│   ├── index.html             # Entry point de la Pokédex TypeDex
│   ├── style-guide.html       # Guía de estilos visual del diseño
│   ├── css/
│   │   ├── styles.css         # Estilos principales de la app
│   │   └── about.css          # Estilos de la vista "Acerca de" (diagrama de pipeline)
│   ├── js/
│   │   ├── app.js             # Lógica principal: sidebar, detalle, rightbar, filtros
│   │   ├── about.js           # Renderiza el diagrama interactivo del pipeline
│   │   ├── type-icons.js      # SVG icons por tipo (window.TYPE_ICONS, typeIcon())
│   │   └── type-system.js     # Datos de tipos: colores, conceptos, elementos (window.TYPE_SYSTEM)
│   ├── data/
│   │   └── bundle.json        # Bundle generado por 10_bundle_builder.py (allPokemon, types, transformations, pokemonMeta)
│   └── outputs/
│       └── moves/             # {type}.json — movimientos temáticos curados por tipo (18 archivos)
│
├── debug/                     # Scripts exploratorios aislados (gitignored)
│   └── dbg_*.py               # Experimentos de modelos, prompts, estilos
│
└── todo/                      # Planificación y bitácoras de sesión
    ├── PLAN.md                # Plan de fases del proyecto
    ├── pipeline_architecture.md # Documentación de la arquitectura del pipeline
    ├── bitacora-YYYY-MM-DD.md # Log de sesiones de trabajo
    └── claude-desings/        # Handoffs de Claude Design (zips con prototipos HTML)
```

---

## Flujo del pipeline

```
data/sprites/{id}.png
        │
        ▼
   [E1] 01_pokemon_analyst      → outputs/pokemon/{id}.json
        │
        ▼
   [E2] 02_type_designer        → outputs/types_visual/{type}.json
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
   [C] 03–07 Specialists (×5)           [E4] 11_combo_data_writer
        │  pa / ps / pe / na / ns              │
        │  outputs/prompts_parts/              ▼
        │                              outputs/combo_data/{id}_{type}.json
        ▼
   [E3] 08_prompt_conciliator   → outputs/prompts/{id}_{type}.json
        │
        ▼
   [D] 09_image_generator       → outputs/images/{id}_{type}.png
        │
        ▼
   [E5] 10_bundle_builder       → web/data/bundle.json
```

---

## Cómo arrancar

### 1. Iniciar Ollama (Windows PowerShell)

```powershell
$env:OLLAMA_HOST = "0.0.0.0"
$env:OLLAMA_NUM_PARALLEL = "6"
ollama serve
```

### 2. Levantar el container (WSL)

```bash
docker compose up -d
```

### 3. Correr el pipeline

```bash
docker exec pokeaIchemize_pipeline python -m pipeline.batch_runner
```

### 4. Generar el bundle para la web

```bash
PYTHONPATH=. python3 pipeline/10_bundle_builder.py
```

### 5. Abrir la web

```bash
# Desde la raíz del proyecto:
python3 -m http.server 8080
# → http://localhost:8080/web/
```

---

## Parámetros clave (`config.py`)

| Variable | Valor actual | Descripción |
|---|---|---|
| `DEV_POKEMON_IDS` | 50 Pokémon seleccionados | IDs a procesar (vacío = todos) |
| `DEV_TYPE_NAMES` | `["fire","water","ghost","steel","electric","fairy"]` | Tipos a generar |
| `DEV_CLEAN` | `False` | `True` limpia `outputs/` antes de correr |
| `OLLAMA_MODEL` | `qwen3:30b-a3b` | Modelo LLM para agentes de texto |
| `OLLAMA_VISION_MODEL` | `qwen2.5vl:7b` | Modelo vision para E1 |
| `ZIMAGE_MODEL` | `Tongyi-MAI/Z-Image-Turbo` | Modelo de generación de imágenes |
| `IMAGE_WIDTH/HEIGHT` | `512 × 512` | Resolución de sprites generados |
| `ZIMAGE_GUIDANCE` | `0.0` | Guidance scale (modelo distilado) |

---

## Paths de la web (relativos a `web/`)

| Path en `app.js` | Archivo real en el proyecto |
|---|---|
| `data/bundle.json` | `web/data/bundle.json` |
| `outputs/moves/{type}.json` | `web/outputs/moves/{type}.json` |
| `../data/sprites/{id}.png` | `data/sprites/{id}.png` |
| `../outputs/images/{id}_{type}.png` | `outputs/images/{id}_{type}.png` |
| `../outputs/combo_data/{id}_{type}.json` | `outputs/combo_data/{id}_{type}.json` |
| `../outputs/prompts/{id}_{type}.json` | `outputs/prompts/{id}_{type}.json` |
| `../outputs/prompts_parts/{id}_{type}_*.json` | `outputs/prompts_parts/` |
