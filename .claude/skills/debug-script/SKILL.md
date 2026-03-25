---
name: debug-script
description: >
  Defines the workflow for writing and isolating debug or exploratory scripts when
  investigating a bug, testing a specific module, or running experiments. Load this skill
  when the user wants to debug, trace, inspect, or experiment with a specific function
  or behavior. Key triggers: "debug", "investigate", "trace", "why is X failing",
  "let me test this", "exploratory script", "check if X works".
---
# debug-script
# Purpose: Define behavior and rules for debug code and files
# Scope: all exploratory/debug scripts

DEBUG_ROOT_FOLDER:
    - All scratch / exploratory code goes in the top-level directory debug/.
    - The entire debug/ folder is listed in .gitignore. No debug scripts are committed.

FILENAME_CONVENTION:
    - See .claude/rules/file-naming.md for naming files guidance.
    - Pattern: debug_<module>[_<experiment>].py
      • module = name of the pipeline file being debugged (e.g. prompt_gen, img_gen, batch)
      • experiment = optional short slug for the debug purpose
    - Examples:
        debug_prompt_gen_model_comparison.py
        debug_img_gen_cuda_check.py
        debug_batch_skip_logic.py

DEBUG_WRITING_RULES:
    - Each script targets a specific module or function in pipeline/; keep that link explicit in the name.
    - Use clear section headers and variable names to describe your intent.
    - Add inline comments to document key findings or dead ends.
    - Temporary logging and print statements are allowed.
    - Keep code readable — think of it as an experiment log.

CLEAN_CODE_PRINCIPLE:
    - Temporary print(), logging.debug(), flags, or conditional logic may be added inside
      pipeline/ files only during active debugging.
    - Before committing: all debugging logic must be removed from pipeline/ files.
    - Final pipeline code must be clean, minimal, and production-ready.
    - All deep debugging and verbose outputs must live in debug/ scripts only.

ISOLATION_AND_ARTIFACTS:
    - Debug scripts must never be imported by pipeline/ code.
    - Any large files or outputs created during debugging go to debug/.cache/ (also git-ignored).

PROMOTION_PATH:
    - If a debug script reveals a real bug worth preserving as a regression check,
      document the fix in the commit message.
    - Remove or archive the original debug script after the bug is resolved.
