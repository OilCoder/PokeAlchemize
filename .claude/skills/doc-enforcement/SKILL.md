---
name: doc-enforcement
description: >
  Enforces standardized Google Style docstrings and module-level documentation for all
  public Python functions, methods, and classes. Load this skill when the user asks to
  add, write, update, or review docstrings or module documentation. Key triggers:
  "add docstring", "document this function", "write docs", "update docstring",
  "document the module", "missing documentation".
---
# doc-enforcement
# Purpose: Enforce standardized documentation using Google Style docstrings.
# Scope: all public Python code in pipeline/

DOCSTRING_REQUIRED:
  - All public functions, methods, and classes must include a Google Style docstring.
  - Private functions (starting with '_') require a docstring if they contain nontrivial logic.

MODULE_HEADER_DOCSTRING:
  - Every Python file under pipeline/ must begin with a top-level docstring.
  - This docstring must serve as a concise summary of the module's purpose.
  - It may contain:
      • A short description of the file's overall goal (1–3 lines)
      • An optional bullet list of major functions or classes
      • Optional usage context (e.g. "Called by batch_runner.py")
  - Keep it under 100 words. Avoid excessive detail or inline implementation logic.

DOCSTRING_STRUCTURE:
  - Must include (if applicable):
    • One-line summary describing behavior.
    • "Args:" section with parameter names, types, and descriptions.
    • "Returns:" section with return type and explanation.
    • "Raises:" section for explicitly raised exceptions.

STYLE_RULES:
  - Must match Google Style formatting (headers, indentation, alignment).
  - Do not mix with NumPy or reStructuredText formats.
  - Avoid vague terms like "does something" or "helper function".
  - If a function has no parameters or return value, still explain what it does.

CONSISTENCY_RULES:
  - Docstring must reflect actual behavior, not intentions or placeholders.
  - Do not duplicate content across sections.
  - Keep docstrings concise, specific, and informative.

ENFORCEMENT_SCOPE:
  - Applies to all files under pipeline/ and config.py.
  - Functions without docstrings may be excluded from generated documentation.
