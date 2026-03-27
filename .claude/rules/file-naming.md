---
description: Enforces consistent file naming conventions across all file types in the project — Python scripts, JSON data files, generated output images, and web assets.
---
# file-naming
# Purpose: Enforce consistent file naming across project
# Scope: all file types (source, data, outputs, web)

All files in the project must follow consistent and descriptive naming conventions
to ensure discoverability, clarity, and traceability across the codebase.

GENERAL_CONVENTIONS:
  - Use snake_case for all Python files: lowercase letters with underscores.
  - Filenames must reflect the purpose or main component of the file.
  - Avoid generic names like data.py, utils.py unless scoped in clearly named folders.

EXECUTION_ORDER_NAMING:
  - Orchestrator files (main entry points, runners, workflows) use plain descriptive
    names without numbering.
      Examples: batch_runner.py, main.py, pipeline.py
  - Individual step files that perform a specific task within a workflow are prefixed
    with a zero-padded two-digit number reflecting their execution order:
      {NN}_{descriptive_name}.py
  - The number reflects position in the pipeline, not importance.
  - Only top-level steps are numbered; sub-components or helpers are not.
  - If a step is added between existing steps, renumber all subsequent files to
    maintain a contiguous sequence.

PYTHON_FILES:
  - snake_case, descriptive names.
  - Global configuration files live in the project root.
  - Constants inside config files use UPPER_SNAKE_CASE.

JSON_DATA_FILES:
  - Pattern: <descriptive_name>.json
  - Input data lives in data/.
  - Generated outputs live in outputs/ or a descriptive subfolder.

OUTPUT_IMAGES:
  - Pattern: {id}_{qualifier}.png
      • id = zero-padded identifier (e.g. 001, 025, 150)
      • qualifier = lowercase descriptor, no spaces (e.g. water, fire, ghost)
  - Location: outputs/images/ or equivalent subfolder.

WEB_FILES:
  - Descriptive fixed names: index.html, style.css, app.js
  - Assets in a dedicated subfolder if needed.
