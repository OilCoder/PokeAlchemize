---
name: phase-executor
description: >
  Use when executing a development phase from todo/PLAN.md. Activates
  when the user says "execute phase", "run phase", "work on phase N",
  "implement phase N", or references a specific phase by name or number.
  Reads PLAN.md first, presents an execution plan, waits for approval,
  then implements tasks in order while updating checkboxes. Never touches
  files outside the phase scope.
---

# phase-executor

## Before writing any code

1. Read `todo/PLAN.md` completely.
2. Identify the requested phase and extract its task list.
3. Present a short plan:
   - Files to create or modify
   - Order of execution
   - Any ambiguity that needs user input
4. Wait for explicit user approval before proceeding.

## Execution rules

SCOPE:
- Only create or modify files listed in the phase tasks.
- Never touch files from other phases.
- If a required file from a previous phase is missing, stop and inform
  the user before continuing.

ORDER:
- Execute tasks in the order they appear in PLAN.md.
- Complete each task fully before moving to the next.
- Mark each task as `- [x]` in PLAN.md immediately after completing it.

CODE:
- Follow all rules in `.claude/rules/`.
- snake_case for all Python files and variables.
- Google Style docstrings on all public functions.
- No print() in production code — use logging per logging-policy.md.
- Functions under 50 lines; extract helpers for multi-step logic.

PROJECT CONVENTIONS:
- Images: `outputs/images/{id_pokemon}_{tipo}.png` (e.g. `025_water.png`)
- Data: static JSON only, no database.
- Batch runner must skip existing images (resumable).
- Ollama runs on host: `host.docker.internal:11434`
- GPU: RTX 4080, CUDA enabled.

## After completing a phase

1. Mark the phase title as `(COMPLETED)` in PLAN.md.
2. Report:
   - Files created
   - Functions implemented
   - Decisions made during execution
3. Flag anything that needs user review before starting the next phase.
