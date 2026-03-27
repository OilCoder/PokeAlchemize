---
name: test
description: >
  Defines Pytest naming conventions, test isolation standards, and structure for writing
  automated tests. Load this skill when the user asks to write, create, add, or update
  test files or test cases. Key triggers: "write a test", "add tests", "create test case",
  "pytest", "unit test", "test this function", "test coverage".
---
# test
# Purpose: Defines test writing rules, naming conventions, and structure for Pytest-based test files.
# Scope: testing

TEST_ROOT_FOLDER:
  - All automated tests live inside the top-level directory tests/.
  - Pytest discovers files recursively; sub-folders are allowed if needed.
  - Temporary or debugging scripts must be named sandbox_*.py so Pytest ignores them.

FILENAME_CONVENTION:
  - See .claude/rules/file-naming.md for naming files guidance.
  - Pattern: test_<NN>_<module>[_<purpose>].py
    • NN = two-digit index (00–99) for natural order
    • module = name of the pipeline file tested (without .py)
    • purpose = optional tag for variant or special case
  - Examples:
      test_01_prompt_generator.py
      test_02_image_generator_cuda.py
      test_03_batch_runner_skip_logic.py

TEST_WRITING_RULES:
  - Each test file must target a single function, class, or module.
  - Test functions follow the format: def test_<method>_<case>().
  - Use assert statements tied to expected behavior.
  - Prefer isolated logic; avoid shared state unless using fixtures.
  - Use @pytest.mark.<tag> to group tests (e.g. integration, gpu, slow).
  - Keep tests simple, readable, and focused on one thing per test.
  - For GPU-dependent tests (image generation), mark with @pytest.mark.gpu.

INDEPENDENCE_AND_ORDERING:
  - Tests must be self-contained; execution order should not matter.
  - The numeric prefix serves only for natural sorting and must never create dependencies.

CACHE_AND_ARTIFACTS:
  - Do not commit __pycache__/ or .pytest_cache/; ensure they are listed in .gitignore.
  - Test fixtures that generate images must write to a temp dir, not outputs/.
