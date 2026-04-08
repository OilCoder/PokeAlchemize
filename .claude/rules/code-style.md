---
description: Enforces layout, naming, spacing, and step/substep comment structure in all Python source files. Applies universally to every task involving Python code.
---
# Code Style

All generated code must prioritize clarity, simplicity, and directness.

## Function structure

- Every function must have a single, well-defined responsibility.
- Function bodies: ideally under 50 lines.
- Use helper functions if a task has multiple logical steps.

## Minimalism

- Only generate what is strictly necessary to fulfill the request.
- No boilerplate, placeholder code, or speculative structures.
- No future-proof abstractions unless explicitly requested.

## Naming

- `snake_case` for all Python files, variables, and functions.
- Constants: `UPPER_SNAKE_CASE`.
- Avoid generic names (e.g., temp, foo, bar).

## Comments and visual structure

```python
# ----------------------------------------
# Step N — <High-level action>
# ----------------------------------------

# Substep N.M — <Specific sub-action>

# ✅ Validate inputs
# 🔄 Loop through each pokemon
# 💾 Save image to outputs/
```

## Imports and dependencies

- Standard → external → internal grouping.
- Only import what is used.
- No new third-party dependencies without explicit approval.

## Scope discipline

- Never write more than what the request scope defines.
- Avoid solving problems that were not asked.

## Cross-references

- See `logging-policy.md` for print/log guidance.
- See `file-naming.md` for naming conventions.
- See `doc-enforcement.md` for docstring requirements.
