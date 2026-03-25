---
description: Index of all Claude rules and skills in the project. Defines the project structure, rule loading strategy, and enforcement scope for PokeAIchemize.
---
# project-guidelines
# Purpose: Define the role and scope of each rule and skill in the codebase
# Scope: repository-wide

RULE_INDEX:
  Rules (always loaded):
    1. code-style.md        – Layout, naming, spacing, and step/substep structure in Python files.
    2. file-naming.md       – Naming conventions for .py, .json, output images, and web files.
    3. logging-policy.md    – Controls print/logging in *.py; enforces batch runner progress output.
    4. project-guidelines.md – This file: index and enforcement strategy.

  Skills (loaded on demand by task type):
    5. code-change   – Strict editing scope boundaries for modifying existing code.
    6. debug-script  – Workflow for writing and isolating debug/exploratory scripts.
    7. doc-enforcement – Standards for Google Style docstrings and module-level docs.
    8. docs-style    – Format and structure for Markdown documentation files.
    9. test          – Pytest naming conventions, isolation standards, and test structure.
    10. plan-writing.md – Defines format and update rules for todo/ plan files.
    11. phase-executor – Reads and executes a phase from PLAN.md in order,
        with scope enforcement and checkbox updates.

PROJECT_STRUCTURE:
  data/        → JSON data: pokemons.json (150 Pokémon), types.json (18 types + biomes)
  pipeline/    → prompt_generator.py, image_generator.py, batch_runner.py
  outputs/     → images/{id}_{tipo}.png + metadata.json (both gitignored)
  web/         → index.html, style.css, app.js (static frontend, no backend)
  todo/        → PLAN.md and project notes
  config.py    → Global paths, model names, generation parameters

ENFORCEMENT_STRATEGY:
  - All Python changes must comply with code-style and file-naming rules.
  - batch_runner.py must comply with logging-policy (progress + skip logging).
  - Invoke code-change skill when editing existing functions/modules.
  - Invoke doc-enforcement skill when adding or updating docstrings.
  - No formal test suite in this project; test skill available if needed.
  - No debug/ folder; debug-script skill available if exploratory scripts are needed.

TECH_CONSTRAINTS:
  - Everything local — no external APIs, no cloud services.
  - Ollama runs on the host; accessible from Docker via host.docker.internal:11434.
  - Image generation via diffusers + PyTorch on RTX 4080 (CUDA).
  - Web is fully static; reads outputs/metadata.json directly.
