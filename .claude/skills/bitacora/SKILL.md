---
name: bitacora
description: Log the current work session in the project's session log.
argument-hint: "[optional summary message]"
---

# Bitacora (Session Log)

Target file: `todo/bitacora-YYYY-MM-DD.md`

## Procedure

1. Run `git log`, `git diff`, and `git status` to gather context.
2. If file exists, append; if not, create with full template.
3. Write entry with: Technical changes, Design decisions, Pending, Learnings.

## Entry structure

```markdown
## HH:MM — [short summary]

### Technical changes
- modified_file.py — what changed and why

### Design decisions
- [Decision] — [reason]

### Pending
- [ ] Task

### Learnings
- [Something discovered]
```

## Rules

- Language: Spanish for prose, English for code/file names.
- No fabrication — only record what actually happened.
- Accumulate: multiple entries per day allowed.
