---
description: >
  Defines how plans are written and updated in todo/. Apply when the user
  asks to create a plan, update a plan, or add a new phase. Also applies
  when an agent completes tasks and needs to update PLAN.md.
---

# plan-writing

## Plan structure

Every plan lives in `todo/` as a Markdown file.
- General project plan: `todo/PLAN.md`
- Phase-specific plans (if needed): `todo/phase_XX_<name>.md`

## File format

Use this structure, nothing more:

```
# <Project or Phase Name>

## Goal
One sentence. What does this plan accomplish?

## Stack (only in PLAN.md)
Simple table: Layer | Technology

## Structure (only in PLAN.md)
Folder tree showing key paths and their purpose.

## Phases

### Phase N — <Name>
- [ ] Task description (file or module it targets)
- [ ] Task description
- [ ] Task description

### Phase N+1 — <Name>
- [ ] ...

## Conventions
Short bullet list of naming rules or constraints relevant to this plan.
```

## Writing rules

- Use plain Markdown only. No HTML, no frontmatter, no badges.
- Tasks use `- [ ]` checkboxes. One task = one action.
- Each task should name the file or module it targets.
- No sub-tasks, no nested checkboxes. Keep it flat.
- No status tables, no emoji columns, no progress bars.
- Avoid vague tasks like "improve X" or "refactor Y". Be specific.
- Phases must be independent — a phase should not depend on
  assumptions from another phase unless explicitly stated.

## When creating a plan

1. Ask the user: goal, stack, and rough phases if not provided.
2. Draft the plan following the format above.
3. Show the draft and wait for approval before saving.
4. Save only to `todo/` once approved.

## When updating a plan

- Mark completed tasks as `- [x]` immediately after finishing them.
- Do not delete tasks, even completed ones.
- Do not add new tasks to a phase without user approval.
- If a phase is fully completed, add `(COMPLETED)` to the phase title.
- Never rewrite or reformat existing content — only update checkboxes
  and phase titles.
