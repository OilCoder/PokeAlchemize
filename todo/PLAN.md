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
| LLM (prompts) | Ollama (modelo a definir en Phase 2) |
| Imagen        | diffusers + PyTorch (SDXL / FLUX.1, a definir en Phase 3) |
| Datos Pokémon | PokéAPI (sprites oficiales)         |
| Web           | HTML / CSS / JS estático            |
| Orquestación  | Python puro                         |
| Aislamiento   | Docker + docker-compose             |

## Structure
```
PokeAIchemize/
├── data/
│   ├── pokemons.json          # 150 pokémon (id, nombre, tipos, sprite_url)
│   ├── types.json             # 18 tipos oficiales
│   └── styles.json            # 5 estilos visuales con descriptores
├── pipeline/
│   ├── pokemon_agent.py       # describe el Pokémon adaptado al tipo
│   ├── biome_agent.py         # describe el hábitat de la combinación
│   ├── style_agent.py         # selecciona estilo desde styles.json
│   ├── scene_conciliador.py   # fusiona pokemon_desc + biome_desc → escena
│   ├── style_conciliador.py   # fusiona escena + style_desc → prompt final
│   ├── image_generator.py     # diffusers → imágenes PNG
│   └── batch_runner.py        # orquesta todo secuencialmente
├── outputs/
│   ├── images/                # {id_pokemon}_{tipo}.png
│   └── prompts/               # un JSON por Pokémon: {id}.json (18 entradas c/u)
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

### Phase 1 — Datos (COMPLETED)
- [x] `data/pokemons.json`: 150 Pokémon vía PokéAPI (id, nombre, tipos, sprite_url)
- [x] `data/types.json`: 18 tipos oficiales
- [x] `data/styles.json`: 5 estilos visuales con descriptores para el modelo de imagen

### Phase 2 — Prompt Generator
- [x] `config.py`: definir modelo Ollama, estilo visual consistente y paths
- [x] `pipeline/pokemon_agent.py`: describe visualmente el Pokémon adaptado al tipo objetivo
- [x] `pipeline/biome_agent.py`: describe el hábitat/entorno específico para esa combinación (pokemon, target_type)
- [x] `pipeline/style_agent.py`: selecciona el estilo artístico apropiado desde styles.json para la combinación
- [x] `pipeline/scene_conciliador.py`: fusiona pokemon_desc + biome_desc en una descripción de escena coherente
- [x] `pipeline/style_conciliador.py`: fusiona scene_desc + style_desc en el prompt final para el modelo de imagen
- [ ] Experimento: probar 3-4 modelos Ollama con 1 combinación de prueba y elegir el mejor
- [ ] Generar los 2,700 prompts y guardar en `outputs/prompts/{id}.json` (un archivo por Pokémon)

### Phase 3 — Image Generator
- [ ] Decidir entre SDXL y FLUX.1 según calidad/velocidad deseada
- [ ] `pipeline/image_generator.py`: cargar modelo una sola vez en memoria
- [ ] `pipeline/image_generator.py`: iterar `outputs/prompts/` y generar imagen 768×768 por entrada
- [ ] `pipeline/image_generator.py`: skip si la imagen ya existe (reanudable)

### Phase 4 — Batch Runner
- [ ] `pipeline/batch_runner.py`: ejecutar Phase 2 completa (todos los prompts) antes de Phase 3
- [ ] `pipeline/batch_runner.py`: ejecutar Phase 3 completa (todas las imágenes) con modelo cargado una vez
- [ ] `pipeline/batch_runner.py`: log de progreso con tqdm, skip y errores sin detener el batch

### Phase 5 — Web Pokédex
- [ ] `web/index.html`: grid de los 150 Pokémon navegable
- [ ] `web/app.js`: al seleccionar un Pokémon, cargar su `{id}.json` y mostrar sprite original + 18 versiones reimaginadas
- [ ] `web/style.css`: diseño estilo Pokédex
- [ ] Nombre del Pokémon y tipo visible en cada tarjeta

## Conventions
- Imágenes: `outputs/images/{id_pokemon}_{tipo}.png` (ej. `025_fire.png`)
- Prompts: `outputs/prompts/{id}.json` — 18 entradas por archivo, campos: pokemon_id, pokemon_name, original_types, target_type, pokemon_desc, biome_desc, style_desc, final_prompt, image_path, generated
- Prompts en inglés (idioma por defecto de los modelos de imagen)
- Sin base de datos: todo en JSON estático
- Sin servidor backend: la web carga el JSON del Pokémon seleccionado bajo demanda
