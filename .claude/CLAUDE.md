# PokeAIchemize

Proyecto personal para reimaginar los 150 Pokémon de Gen 1 cambiando su tipo base.
Genera 2,700 sprites reimaginados (150 Pokémon × 18 tipos) y los muestra en una web estilo Pokédex.

## Stack
- LLM: Ollama local (host, accesible via host.docker.internal:11434)
- Sprite: FLUX.1-Kontext-dev + WiroAI/pokemon-flux-lora (RTX 4080)
- Fondo: FLUX.1-dev + inpainting/outpainting
- Web: HTML/CSS/JS estático (sin servidor backend)
- Todo es local — sin APIs externas, sin servicios cloud

## Estructura
```
data/        → pokemons.json, types.json, styles.json, sprites/
pipeline/    → 01–09 agents + batch_runner.py
outputs/     → images/{id}_{tipo}.png + prompts/{id}.json
web/         → index.html, style.css, app.js
config.py    → paths, modelos, parámetros globales
todo/        → PLAN.md, bitácoras y notas
debug/       → scripts exploratorios (gitignored)
```

## Rules (siempre activas)

| Rule | Propósito |
|---|---|
| `code-style` | Layout, naming, estructura Step/Substep |
| `file-naming` | Convenciones de nombres y orden de ejecución |
| `code-change` | Alcance y seguridad de ediciones |
| `logging-policy` | Control de print/logging |
| `doc-enforcement` | Docstrings obligatorios |
| `docs-style` | Formato de documentación Markdown |
| `plan-format` | Formato y reglas de actualización de planes |
| `project-guidelines` | Índice, enforcement y modo de validación |

## Skills (bajo demanda)

| Skill | Trigger | Propósito |
|---|---|---|
| `/bitacora` | Post-commit o manual | Registrar sesión en `todo/bitacora-YYYY-MM-DD.md` |
| `/plan-writing` | Manual | Crear/actualizar `todo/PLAN.md` |
| `/phase-executor` | "ejecutar fase N" | Ejecutar fase del plan en orden |
| `/code-change` | "editar esta función" | Edición con scope estricto |
| `/debug` | "debuggear", "investigar" | Scripts aislados en `debug/` |
| `/document` | "documentar módulo" | Generar doc Markdown de un módulo |
| `/doc-enforce` | "revisar docstrings" | Revisar y generar docstrings |
| `/test` | "escribir tests" | Crear tests con Pytest |

## Modo de validación
`warn` — reglas aplicadas, violaciones marcadas sin bloquear.

## Workflow de sesión

### Antes de correr el pipeline
1. Iniciar Ollama en PowerShell (Windows):
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
- `DEV_CLEAN = True` en `config.py` limpia `outputs/` automáticamente al correr `batch_runner.py`
