---
name: phase-executor
description: >
  Use when executing a development phase from todo/PLAN.md. Activates
  when the user says "execute phase", "run phase", "work on phase N",
  "implement phase N", or references a specific phase by name or number.
  Reads PLAN.md first, presents an execution plan, waits for approval,
  then implements tasks in order while updating checkboxes. Never touches
  files outside the phase scope.
argument-hint: "[phase number or name]"
---

# Phase Executor

## Before writing any code

1. Read `todo/PLAN.md` completely.
2. Extract task list for the requested phase.
3. Present a short plan:
   - Files to create or modify
   - Order of execution
   - Any ambiguity that needs user input
4. Wait for explicit user approval before proceeding.

## Execution rules

- Only touch files listed in the phase tasks.
- Never touch files from other phases.
- Execute tasks in PLAN.md order; mark `- [x] (YYYY-MM-DD)` immediately after each.
- Follow all `.claude/rules/` conventions.

## Project conventions

- Images: `outputs/images/{id}_{tipo}.png` (e.g. `025_fire.png`)
- Sprites base: `data/sprites/{id}.png`
- Prompts: `outputs/prompts/{id}.json`
- Ollama: `host.docker.internal:11434`
- GPU: RTX 4080, CUDA. Image model: FLUX.1-Kontext-dev.

## After completing a phase

1. Mark phase title as `(COMPLETED)` in PLAN.md.
2. Report: files created, functions implemented, decisions made.
3. Flag anything needing user review.
4. Suggest `/bitacora` to log the session.
