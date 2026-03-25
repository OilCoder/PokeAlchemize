---
description: Controls use of print() and logging calls in Python files. Allows temporary prints during development but enforces cleanup before commit, with specific rules for the batch runner's progress output.
paths:
  - "**/*.py"
---
# logging-policy
# Purpose: Control use of print and logging across all Python code
# Scope: global (pipeline, config, batch runner)

PRINT_USAGE:
  - Temporary print() statements are allowed during development.
  - All print() calls must be removed before final commits unless:
    • They are part of CLI tools with user-facing output.
    • They serve a critical runtime function (e.g. batch progress summary).

LOGGING_USAGE:
  - Use logging.info, logging.warning, and logging.error for structured output in production.
  - Avoid logging.debug unless the logger is properly configured and output can be filtered.
  - Always use logger = logging.getLogger(__name__) for module-scoped loggers.

BATCH_RUNNER_SPECIFICS:
  - batch_runner.py must show visible progress (tqdm bar preferred).
  - Log when an image is skipped (already exists).
  - Log errors per combination without stopping the full batch.
  - A final summary line (total generated, skipped, failed) is required.

CLEANUP_AND_ISOLATION:
  - Final versions of pipeline/ scripts must not include leftover debug print/log.
  - Treat print/log statements as disposable scaffolding unless approved.
  - Do not add logging.debug() noise to image_generator.py or prompt_generator.py.
