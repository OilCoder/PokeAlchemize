---
description: Enforce standardized docstrings and module-level documentation in all source files
---

# Doc Enforcement

All public functions, methods, and classes must include a docstring.
This rule applies passively to all code Claude generates or modifies.

## Docstring required

- All public functions, methods, and classes must include a docstring.
- Private functions (starting with `_`) require a docstring only if they contain nontrivial logic.
- Docstring format: Google Style.

## Module header

- Every source file must begin with a top-level module docstring.
- Content: concise summary of the module's purpose (1–3 lines).
- May include an optional bullet list of major functions or classes.
- May include optional usage context (e.g., "Called by `batch_runner.py`").
- Keep it under 100 words.

## Docstring structure

Must include (if applicable):

- One-line summary describing behavior (imperative mood).
- `Args:` section with parameter names, types, and descriptions.
- `Returns:` section with return type and explanation.
- `Raises:` section for explicitly raised exceptions.

## Style rules

- Do not mix Google Style with NumPy or reStructuredText formats.
- Avoid vague terms like "does something", "helper function", "processes data".
- If a function has no parameters or return value, still explain what it does.

## Consistency

- Docstrings must reflect actual behavior, not intentions or placeholders.
- When modifying a function, update its docstring if the behavior changed.

## Enforcement scope

- Applies to all files under `pipeline/` and `config.py`.

## Cross-references

- See `doc-enforce/SKILL.md` for the on-demand review and enforcement workflow.
- See `docs-style.md` for Markdown documentation standards.
