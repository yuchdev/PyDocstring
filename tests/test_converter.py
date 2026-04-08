"""Tests for the converter module."""
import pytest
from pathlib import Path
from pydocstring.converter import convert_file, convert_project, detect_docstring_style
from pydocstring.models import DocstringStyle


def test_detect_docstring_style_google():
    text = "Args:\n    x (int): A number."
    result = detect_docstring_style(text)
    assert result.style == DocstringStyle.GOOGLE


def test_detect_docstring_style_sphinx():
    text = ":param x: A number.\n:type x: int"
    result = detect_docstring_style(text)
    assert result.style == DocstringStyle.SPHINX


def test_convert_file_google_to_sphinx(tmp_path):
    source = '''def foo(x):
    """Do something.

    Args:
        x (int): A number.

    Returns:
        bool: True.
    """
    pass
'''
    py_file = tmp_path / "test.py"
    py_file.write_text(source)

    result = convert_file(py_file, target_style="sphinx")
    assert result.changed
    assert ":param x:" in result.converted_source
    assert result.error is None


def test_convert_file_dry_run(tmp_path):
    source = '''def foo(x):
    """Do something.

    Args:
        x (int): A number.
    """
    pass
'''
    py_file = tmp_path / "test.py"
    py_file.write_text(source)

    result = convert_file(py_file, target_style="sphinx", dry_run=True)
    assert result.changed
    # File should not be modified in dry_run mode
    assert py_file.read_text() == source


def test_convert_file_no_change(tmp_path):
    source = '''def foo(x):
    """Do something.

    :param x: A number.
    :type x: int
    """
    pass
'''
    py_file = tmp_path / "test.py"
    py_file.write_text(source)

    result = convert_file(py_file, target_style="sphinx")
    assert not result.changed


def test_convert_project(tmp_path):
    source1 = '''def foo(x):
    """Do something.

    Args:
        x (int): A number.
    """
    pass
'''
    source2 = '''def bar(y):
    """Do another thing.

    Args:
        y (str): A string.
    """
    pass
'''
    (tmp_path / "foo.py").write_text(source1)
    (tmp_path / "bar.py").write_text(source2)

    result = convert_project(tmp_path, target_style="sphinx", dry_run=True)
    assert result.files_processed == 2
    assert result.files_changed == 2
