from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pytest

from tests import PROJECT_ROOT
from lint_rules import check_file, RuleViolation



def iter_python_files() -> Iterable[Path]:
    """Yield all project top-level *.py files in covered_dirs (no subfolders)."""
    covered_dirs = [
        PROJECT_ROOT / "src"
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "tests" / "lint"
    ]
    for dir_path in covered_dirs:
        if not dir_path.is_dir():
            continue
        for path in dir_path.glob("*.py"):
            parts = set(path.parts)
            if {".venv", "venv", ".git", "__pycache__", "build", "dist"} & parts:
                continue
            yield path


def test_code_style_custom_rules():
    """
    [Integration] Custom lint rules: all covered Python files pass custom linting checks.

    Scenario:
        Given a set of project Python files in covered directories.
        When check_file() runs all custom lint rules (X001-X010).
        Then no RuleViolation instances are returned.
        And all code follows the project's custom style guidelines.

    Boundaries:
        - Real: AST parsing, lint rule implementations, file I/O
        - Scope: source code, tests
        - Covers: broad exceptions, muted exceptions, local imports, docstrings, return types, logging, import suppression, union types.

    On failure, first check:
        - The specific violation message and line number in the output
        - Whether a recent code change introduced the violation
        - The lint_rules.py module for the rule implementation
        - Whether the rule should be adjusted or the code should be fixed.
    """
    violations: List[RuleViolation] = []

    for path in iter_python_files():
        violations.extend(check_file(path))

    if violations:
        lines = [
            f"{v.filename}:{v.lineno}:{v.col_offset}: {v.code} {v.message}"
            for v in violations
        ]
        msg = "Custom lint violations found:\n" + "\n".join(lines)
        pytest.fail(msg)
