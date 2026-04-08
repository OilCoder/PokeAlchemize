# PokeAIchemize

Proyecto personal para reimaginar los 150 Pokémon de Gen 1 cambiando su tipo base.
Genera 2,700 imágenes (150 Pokémon × 18 tipos) y las muestra en una web estilo Pokédex.

## Stack
- LLM: Ollama local (corre en el host, accesible via host.docker.internal:11434)
- Imagen: diffusers + PyTorch, RTX 4080, SDXL o FLUX.1
- Web: HTML/CSS/JS estático (sin servidor backend)
- Todo es local — sin APIs externas, sin servicios cloud

## Estructura
```
data/        → pokemons.json (150), types.json (18 tipos)
pipeline/    → prompt_generator.py, image_generator.py, batch_runner.py
outputs/     → images/{id}_{tipo}.png + metadata.json
web/         → index.html, style.css, app.js
config.py    → paths, modelos, parámetros globales
todo/        → PLAN.md y notas
```

## Convenciones clave
- Imágenes: outputs/images/{id_pokemon}_{tipo}.png (ej. 025_water.png)
- Datos: JSON estático, sin base de datos
- El batch runner debe ser reanudable (skip si imagen ya existe)
- Ver .claude/rules/ para reglas detalladas de estilo y naming

## Workflow de sesión

### Antes de correr el pipeline
1. Iniciar Ollama en PowerShell (Windows) con:
   ```powershell
   $env:OLLAMA_HOST = "0.0.0.0"
   $env:OLLAMA_NUM_PARALLEL = "6"
   ollama serve
   ```
2. Levantar el contenedor desde WSL:
   ```bash
   docker compose up -d
   ```

### En fase de desarrollo
- Borrar siempre outputs/images/, outputs/prompts/ y outputs/pipeline/ antes de cada corrida
- DEV_CLEAN = True en config.py aplica esto automáticamente al correr batch_runner.py
