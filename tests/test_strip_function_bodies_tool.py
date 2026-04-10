"""Tests for the strip_function_bodies tool."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tests import PROJECT_ROOT


TOOL_PATH = PROJECT_ROOT / "tools" / "strip_function_bodies.py"
spec = importlib.util.spec_from_file_location("strip_tool", TOOL_PATH)
strip_tool = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = strip_tool
spec.loader.exec_module(strip_tool)


def test_strip_function_bodies_keeps_docstring_and_replaces_with_pass():
    """[Unit] strip_function_bodies: strip_function_bodies preserves docstrings and replaces bodies with pass.

    Scenario: Call strip_function_bodies on source with two functions containing docstrings and code.
    Boundaries: Function and method bodies with docstrings; code replaced by pass, docstrings kept.
    On failure, first check: strip_function_bodies docstring detection and body replacement logic.
    """
    source = '''
def foo(a, b):
    """Compute something."""
    result = a + b
    return result

class Service:
    def run(self):
        """Run the service."""
        value = 42
        return value
'''

    rewritten = strip_tool.strip_function_bodies(source)

    assert '"""Compute something."""' in rewritten
    assert '"""Run the service."""' in rewritten
    assert "result = a + b" not in rewritten
    assert "value = 42" not in rewritten
    assert "    pass" in rewritten


def test_rewrite_paths_updates_python_files(tmp_path: Path):
    """[Unit] strip_function_bodies: rewrite_paths rewrites Python files and reports changed count.

    Scenario: Call rewrite_paths on a directory containing one Python file with a body.
    Boundaries: Single .py file with a return statement; body replaced by pass, docstring kept.
    On failure, first check: rewrite_paths file discovery, strip_function_bodies, and changed_files count.
    """
    py_file = tmp_path / "sample.py"
    py_file.write_text(
        "def f():\n    \"\"\"Doc.\"\"\"\n    return 1\n",
        encoding="utf-8",
    )

    result = strip_tool.rewrite_paths([tmp_path])

    updated = py_file.read_text(encoding="utf-8")
    assert result.changed_files == 1
    assert result.renamed_files == 0
    assert "return 1" not in updated
    assert '"""Doc."""' in updated
    assert "pass" in updated


def test_rewrite_paths_can_rename_files_by_pattern(tmp_path: Path):
    """[Unit] strip_function_bodies: rewrite_paths renames files according to the given pattern.

    Scenario: Call rewrite_paths with a rename_pattern and start_index on a directory with two files.
    Boundaries: Two .py files; renamed to sequential pattern names; bodies stripped, renamed_files counted.
    On failure, first check: rewrite_paths rename_pattern substitution and file rename logic.
    """
    alpha = tmp_path / "alpha.py"
    beta = tmp_path / "beta.py"
    alpha.write_text("def a():\n    return 1\n", encoding="utf-8")
    beta.write_text("def b():\n    return 2\n", encoding="utf-8")

    result = strip_tool.rewrite_paths(
        [tmp_path],
        rename_pattern="test_sphinx_doc_{NNN}.py",
        start_index=7,
    )

    assert result.changed_files == 2
    assert result.renamed_files == 2

    renamed = sorted(p.name for p in tmp_path.glob("*.py"))
    assert renamed == ["test_sphinx_doc_007.py", "test_sphinx_doc_008.py"]

    for file_name in renamed:
        content = (tmp_path / file_name).read_text(encoding="utf-8")
        assert "return" not in content
        assert "pass" in content
