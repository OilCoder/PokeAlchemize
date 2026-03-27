---
name: docs-style
description: >
  Defines the required format, structure, and sections for Markdown documentation files.
  Load this skill when the user asks to write, update, or review a Markdown document,
  README, or technical spec. Key triggers: "write documentation", "create a doc",
  "update the README", "document this module", "write a spec", "markdown doc".
---
# docs-style
# Purpose: Define standards for documentation files
# Scope: all Markdown documents

DOCS_ROOT_FOLDER:
    - Documentation files live in todo/ (project notes and plans) or in the project root.
    - No docs/ subfolder in this project.
    - Auto-generated content (e.g. metadata.json) must not be placed in documentation.

FILENAME_CONVENTION:
    - See .claude/rules/file-naming.md for naming guidance.
    - Pattern: <NN>_<topic>[_<scope>].md
      • NN = optional numeric prefix for ordering (00–99)
      • topic = what the document covers
      • scope = optional detail (e.g. setup, architecture, api)

DOC_WRITING_RULES:
    - Each document must reflect the actual behavior of the code — not future plans or assumptions.
    - Every technical document should include the following sections where applicable:

REQUIRED_SECTIONS:
    1. Title and Purpose
        - Start with a single sentence summarizing the module's or document's role.
    2. Workflow Description
        - Describe the sequence of operations performed.
        - Use numbered steps or descriptive text.
        - Include a Mermaid diagram using `flowchart TD` or `graph LR` if applicable.
    3. Inputs and Outputs
        - List each parameter with name, type, and purpose.
        - Describe expected output(s) and their structure.
    4. Code Reference
        - Always include the source module path (e.g., `Source: pipeline/batch_runner.py`)

STYLE:
    - Write clearly and concisely. Use short paragraphs, bullet points, and examples when helpful.
    - Document only what exists in the current version of the code. Avoid TODOs and speculative notes.
    - PLAN.md in todo/ is the exception: it documents planned (not yet built) functionality.
