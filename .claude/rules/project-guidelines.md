---
description: Project-level index of rules, skills, enforcement strategy, and tech constraints for PokeAIchemize
---
# Project Guidelines

## Rules index

| Rule | Propósito |
|---|---|
| `code-style.md` | Layout, naming, estructura Step/Substep |
| `file-naming.md` | Convenciones de nombres y orden de ejecución |
| `code-change.md` | Alcance y seguridad de ediciones |
| `logging-policy.md` | Control de print/logging |
| `doc-enforcement.md` | Docstrings obligatorios en pipeline/ |
| `docs-style.md` | Formato de documentación Markdown |
| `plan-format.md` | Formato y reglas de actualización de planes |

## Skills index

| Skill | Propósito |
|---|---|
| `/bitacora` | Registrar sesión en `todo/bitacora-YYYY-MM-DD.md` |
| `/plan-writing` | Crear/actualizar planes en `todo/` |
| `/phase-executor` | Ejecutar fase del plan en orden con checkboxes |
| `/code-change` | Edición con scope estricto |
| `/debug` | Scripts aislados de exploración en `debug/` |
| `/document` | Generar documentación Markdown de un módulo |
| `/doc-enforce` | Revisar y generar docstrings faltantes |
| `/test` | Crear tests Pytest para módulos |

## Validation mode
`warn` — reglas aplicadas, violaciones marcadas. Cambiar a `strict` antes de producción.

## Project structure

```
data/        → pokemons.json, types.json, styles.json, sprites/
pipeline/    → 01_morph_agent.py … 09_background_generator.py, batch_runner.py
outputs/     → images/{id}_{tipo}.png, prompts/{id}.json (gitignored)
web/         → index.html, style.css, app.js
config.py    → paths, modelos, parámetros
todo/        → PLAN.md y bitácoras
debug/       → scripts exploratorios (gitignored)
```

## Tech constraints
- Todo local — sin APIs externas, sin servicios cloud.
- Ollama en el host: `host.docker.internal:11434`.
- Generación de imágenes: diffusers + PyTorch, RTX 4080, CUDA.
- Web completamente estática: carga JSON bajo demanda, sin backend.
- Imágenes y prompts en `outputs/` (gitignored).
