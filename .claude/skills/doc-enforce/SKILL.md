---
name: doc-enforce
description: >
  Enforces standardized Google Style docstrings and module-level documentation for all
  public Python functions, methods, and classes. Load this skill when the user asks to
  add, write, update, or review docstrings or module documentation. Key triggers:
  "add docstring", "document this function", "write docs", "update docstring",
  "document the module", "missing documentation".
argument-hint: "[file to review]"
---

# Doc Enforce

## Procedure

1. Read the complete file; list all functions/classes with/without docstrings.
2. Report status (✅/❌ per item).
3. Generate missing docstrings in Google Style.
4. Add module header if missing.

## Rules

- Docstrings must reflect actual behavior.
- Do not mix formats (Google Style only).
- Private functions only need docstrings if nontrivial logic.
- Do not modify existing docstrings without approval — only report inconsistencies.
- Scope: all files under `pipeline/` and `config.py`.
