from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "strip_function_bodies.py"
spec = importlib.util.spec_from_file_location("strip_tool", TOOL_PATH)
strip_tool = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = strip_tool
spec.loader.exec_module(strip_tool)


def test_strip_function_bodies_keeps_docstring_and_replaces_with_pass() -> None:
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


def test_rewrite_paths_updates_python_files(tmp_path: Path) -> None:
    py_file = tmp_path / "sample.py"
    py_file.write_text(
        "def f():\n    \"\"\"Doc.\"\"\"\n    return 1\n",
        encoding="utf-8",
    )

    changed = strip_tool.rewrite_paths([tmp_path])

    updated = py_file.read_text(encoding="utf-8")
    assert changed == 1
    assert "return 1" not in updated
    assert '"""Doc."""' in updated
    assert "pass" in updated
