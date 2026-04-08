---
name: document
description: >
  Defines the required format, structure, and sections for Markdown documentation files.
  Load this skill when the user asks to write, update, or review a Markdown document,
  README, or technical spec. Key triggers: "write documentation", "create a doc",
  "update the README", "document this module", "write a spec", "markdown doc".
argument-hint: "[file or module to document]"
---

# Document

## Procedure

1. Read the complete source file.
2. Create doc in `todo/`, named `NN_<slug>.md`.
3. Required sections: Purpose, Workflow (+ Mermaid if complex), Inputs/Outputs, Math (if applicable), Code Reference.

## Rules

- Document only what exists — no plans or assumptions.
- Each document must be self-contained.
- Avoid TODOs and speculative notes.
- Source reference: always include `Source: pipeline/<file>.py`.
