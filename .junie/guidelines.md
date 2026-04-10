# Development Guidelines for PyDocstring

This document provides project-specific information for developers working on ActiveListener.

## 1. Python and tooling

- Target Python **3.12+**; follow the existing project layout.
- Use **pytest** for tests, **ruff** for linting, and **mypy** for type checking where practical.

## 2. Scope

- Operate only on files that belong to this repository.
- Respect the existing file style
- Follow local conventions in a file while still honoring the project guidelines at the end of this document.

## 3. Editing behavior

- When generating code:
  - Place new tests under `tests/` mirroring the module path.
  - Keep imports, naming, and structure consistent with nearby code.
  - Run `pytest -q` after completing each code generation. Do not report complete until the test suite passes.
- When refactoring:
  - Propose small, explicit transformations (rename, extract function, move helper) instead of opaque changes.
  - Preserve public APIs unless the user explicitly asks to change them.
  - Run `pytest -q` after completing each refactoring.  Do not report complete until the test suite passes.
- Do not reformat whole files or re-order imports unless the user requests it or the file is clearly being cleaned up.

## 4. Code Conventions

- Use modern **type hints everywhere** in new or heavily modified code; missing types are treated as technical debt.
- Use **f-strings** for formatting; do not introduce new `%%` formatting.
- Avoid broad exception handlers:
  - No bare `except:`
  - No `except Exception:` unless at a clearly documented top-level boundary.
- Avoid trivial statements like `-> None`
- Do not suppress exceptions, avoid `pass`, `continue`, or `break`; the least you can do is log the exception with context.
- Import modules only in global scope; do not import inside functions or classes unless necessary to avoid circular imports or reduce startup time.
- Follow existing naming conventions in the codebase; do not introduce new styles.
- Implement docstring for each function, class, and module using the existing style (e.g., Google style, NumPy style) found in the file. Do not introduce new docstring styles.
- Use special docstring style for tests:
  - Declare the type of test in the beginning of docstring: `[Unit]`, `[Integration]`, `[Mock]`, `[End-to-End]`
  - Describe the expected outcome using descriptors: `Scenario:`, `Boundaries:`, `Expected:`, `On failure, first check:`

## 5. Tests and safety

- Encourage the user to run `pytest` for affected modules.
- When tests fail:
  - Point to the failing assertions and propose minimal fixes.
  - Don't "fix" tests by weakening assertions and adding exceptions to the rule.
- When changing behavior, **update or add tests** in the appropriate `tests/` module.
- Keep changes **small and focused**; avoid drive-by refactors and mass reformatting.
- Log failures and edge cases clearly; never silently ignore exceptions.
- Do not change public APIs or story data contracts (JSON/graph schemas, scripting contexts) without updating call sites, tests, and docs together.
- Test runner: Project uses pytest. Configuration is in `pytest.ini` and `pyproject.toml` (`[tool.pytest.ini_options]` mirrors the defaults). Key points:
  - `testpaths = tests`
  - Discovery patterns: files `test_*.py`, classes `Test*`, functions `test_*`
  - Python path: `src` is inserted first by `tests/conftest.py`, then project root, then tests
  - Custom markers: `@pytest.mark.scripting`, `@pytest.mark.voice_pipeline_int`
  - Some noisy third‑party warnings are filtered.
- Running tests:
  - All: `pytest -q`
  - Single file: `pytest -q tests/path/to/test_file.py`
  - Adding new tests: Place under `tests/` and follow discovery patterns.

## 6. AI Protection Policy

The following files are **AI-PROTECTED** and must **NEVER** be edited by Junie or any other AI tool:
- `tests/lint/lint_rules.py`
- `tests/lint/test_linting.py`
- Any other files matching `tests/lint/*.py`

These files contain core linting logic and must only be modified manually by a human developer. If changes are needed, please inform the user to make them manually.
