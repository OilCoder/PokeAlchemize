---
description: Controls use of print() and logging calls in Python files. Allows temporary prints during development but enforces cleanup before commit, with specific rules for the batch runner's progress output.
paths:
  - "**/*.py"
---
# Logging Policy

## Print usage

- Temporary `print()` allowed in development; remove before final commits.
- Exceptions: CLI tools, batch progress indicators.

## Logging usage

- Use module-scoped loggers: `logger = logging.getLogger(__name__)`.
- Use `logging.info`, `logging.warning`, `logging.error` for structured output.
- Avoid `logging.debug` unless properly filtered.

## Batch runner specifics

- `batch_runner.py` must show visible progress (tqdm preferred).
- Log when an image is skipped (already exists).
- Log errors per combination without stopping the full batch.
- A final summary line (total generated, skipped, failed) is required.

## Cleanup and isolation

- Final pipeline/ scripts must not include leftover debug print/log.
- Extensive debug output goes into `debug/` scripts only.
