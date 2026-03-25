---
name: code-change
description: >
  Enforces strict editing scope boundaries when modifying existing code. Load this skill
  when the user asks to edit, update, fix, refactor, or change a specific function, class,
  or block in an existing file. Key triggers: "edit this function", "fix this bug",
  "update the logic in", "change how X works", "modify", "refactor".
---
# code-change
# Purpose: Enforce strict editing boundaries for modifying existing code.
# Scope: editing

EDIT_SCOPE:
  - Only modify the exact function, class, or block specified in the request.
  - Do not introduce new functions, utilities, or abstractions unless explicitly asked.
  - Avoid adding code outside the target scope (e.g., logging, debug, helper logic).

STRUCTURAL_INTEGRITY:
  - Preserve the existing order of imports and function declarations unless the user requests reordering.
  - Maintain original indentation, formatting, and comments unless they are directly related to the edit.

MULTI_FILE_CHANGES:
  - Allowed only when the task clearly involves cross-file coordination, such as:
    • Pipeline updates requiring changes across prompt_generator, image_generator, and batch_runner.
    • Web tasks requiring updates to index.html, style.css, and app.js together.
    • Config changes that propagate across pipeline scripts.
  - Constraints:
    • Edit only files directly related to the request.
    • Each change must have a clear reason and impact aligned with the goal.
    • Avoid broad refactors or speculative edits unless explicitly requested.
    • Do not infer relationships between files unless user confirms or implies them.
  - Organize outputs with clear file labels or headers.
  - Show only modified sections; never full files unless requested.

DEBUG_AND_TEST_CODE:
  - Do not insert print(), logging, assertions, or test logic in core code.
  - For bugs, isolate the scenario before editing the main module.
  - See .claude/skills/debug-script/SKILL.md for debug workflow.

COMMENTS:
  - Only modify or add comments tied to the changed logic.
  - Do not rephrase unrelated documentation or annotations.

OUTPUT_FORMAT:
  - Return only modified function/class.
  - Do not show or regenerate unchanged code.
  - Show full file only if explicitly asked by the user.
