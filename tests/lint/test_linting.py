"""Pytest test that runs the custom linter against all project source files."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.lint.linter import check_file

# ---------------------------------------------------------------------------
# Paths to lint
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_DIR = _REPO_ROOT / "src" / "pydocstring"
_TESTS_DIR = _REPO_ROOT / "tests"
_LINT_DIR = _TESTS_DIR / "lint"


def _collect_files() -> list[Path]:
    """Return all Python files that should pass the custom lint checks."""
    files: list[Path] = []
    for path in sorted(_SRC_DIR.rglob("*.py")):
        files.append(path)
    for path in sorted(_TESTS_DIR.glob("*.py")):
        files.append(path)
    return files


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


def test_no_custom_lint_violations() -> None:
    """Fail if any custom lint violation is found in project Python files."""
    all_violations = []
    for path in _collect_files():
        violations = check_file(path)
        all_violations.extend(violations)

    if all_violations:
        lines = [str(v) for v in all_violations]
        pytest.fail("Custom lint violations found:\n" + "\n".join(lines))
