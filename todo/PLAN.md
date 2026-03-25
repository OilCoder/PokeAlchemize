# PokeAIchemize — Plan

## Goal
Reimaginar los primeros 150 Pokémon cambiando su tipo base. Para cada combinación
Pokémon × Tipo se genera una imagen que muestra cómo se vería ese Pokémon si
perteneciera a ese tipo, ambientado en el bioma correspondiente. 150 Pokémon × 18 tipos
= 2,700 imágenes generadas localmente (RTX 4080), pre-generadas en batch; la web solo
muestra resultados estáticos.

## Stack
| Capa          | Tecnología                          |
|---------------|-------------------------------------|
| LLM (prompts) | Ollama (modelo a definir)           |
| Imagen        | diffusers + PyTorch (SDXL / FLUX.1) |
| Datos Pokémon | PokéAPI (sprites oficiales)         |
| Web           | HTML / CSS / JS estático            |
| Orquestación  | Python puro                         |
| Aislamiento   | Docker + docker-compose             |

## Structure
```
PokeAIchemize/
├── data/
│   ├── pokemons.json          # 150 pokémon (nombre, tipos, sprite URL)
│   └── types.json             # 18 tipos + descripción de bioma
├── pipeline/
│   ├── prompt_generator.py    # Ollama → prompt optimizado
│   ├── image_generator.py     # diffusers → imagen PNG
│   └── batch_runner.py        # Itera todas las combinaciones
├── outputs/
│   ├── images/                # {id_pokemon}_{tipo}.png
│   └── metadata.json          # prompts + rutas de imagen
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── config.py                  # Paths, modelos, parámetros
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Phases

### Phase 1 — Datos
- [ ] `data/pokemons.json`: 150 Pokémon con nombre, tipo(s) original(es), URL sprite
- [ ] `data/types.json`: 18 tipos con nombre y descripción de bioma para el prompt

### Phase 2 — Prompt Generator
- [ ] Script `pipeline/prompt_generator.py`
- [ ] Recibe `(pokemon, tipo_objetivo)`, llama a Ollama
- [ ] El LLM genera prompt optimizado para image generation
- [ ] Experimentar con modelos Ollama para encontrar el que genera mejores prompts

### Phase 3 — Image Generator
- [ ] Script `pipeline/image_generator.py`
- [ ] Integrar `diffusers` con SDXL o FLUX.1
- [ ] Output: imagen 768×768 PNG en `outputs/images/`

### Phase 4 — Batch Runner
- [ ] Script `pipeline/batch_runner.py`
- [ ] Itera 150 × 18 combinaciones
- [ ] Skip si la imagen ya existe (reanudar si se interrumpe)
- [ ] Guarda `outputs/metadata.json` con prompt y ruta por cada combinación

### Phase 5 — Web Pokédex
- [ ] Grid de los 150 Pokémon
- [ ] Al seleccionar uno: sprite original + 18 versiones reimaginadas en grid
- [ ] Nombre del Pokémon y nombre del tipo visible en cada tarjeta
- [ ] Filtros por tipo

## Conventions
- Imágenes: `outputs/images/{id_pokemon}_{tipo}.png` (ej. `025_water.png`)
- Sin base de datos: todo en JSON estático
- Sin servidor backend: la web lee `metadata.json` directamente
