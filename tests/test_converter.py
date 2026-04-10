"""Tests for the converter module."""
import pytest
from pathlib import Path
from pydocstring.converter import convert_file, convert_project, detect_docstring_style
from pydocstring.models import DocstringStyle


def test_detect_docstring_style_google():
    """[Unit] converter: detect_docstring_style returns GOOGLE for Google-style text.

    Scenario: Pass a string containing a Google-style 'Args:' section to detect_docstring_style.
    Boundaries: Non-empty string with known Google-style markers.
    On failure, first check: detect_docstring_style logic and DocstringStyle.GOOGLE enum value.
    """
    text = "Args:\n    x (int): A number."
    result = detect_docstring_style(text)
    assert result.style == DocstringStyle.GOOGLE


def test_detect_docstring_style_sphinx():
    """[Unit] converter: detect_docstring_style returns SPHINX for Sphinx-style text.

    Scenario: Pass a string containing Sphinx-style ':param' and ':type' fields to detect_docstring_style.
    Boundaries: Non-empty string with known Sphinx-style markers.
    On failure, first check: detect_docstring_style logic and DocstringStyle.SPHINX enum value.
    """
    text = ":param x: A number.\n:type x: int"
    result = detect_docstring_style(text)
    assert result.style == DocstringStyle.SPHINX


def test_convert_file_google_to_sphinx(tmp_path):
    """[Unit] converter: convert_file converts a Google-style file to Sphinx style.

    Scenario: Write a Python file with a Google-style docstring and convert it to Sphinx style.
    Boundaries: Single function with Args and Returns sections; target_style='sphinx'.
    On failure, first check: convert_file logic, rewriter, and the ':param x:' Sphinx marker presence.
    """
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
    """[Unit] converter: convert_file dry_run does not write changes to disk.

    Scenario: Convert a Google-style file to Sphinx with dry_run=True and verify the file is unchanged.
    Boundaries: Single function file; dry_run=True prevents disk writes.
    On failure, first check: convert_file dry_run flag handling and file I/O logic.
    """
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
    """[Unit] converter: convert_file reports no change when file is already in target style.

    Scenario: Write a Sphinx-style file and convert it to Sphinx; expect no change reported.
    Boundaries: File already in target style; result.changed should be False.
    On failure, first check: style detection logic and the changed flag in the conversion result.
    """
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
    """[Unit] converter: convert_project converts all Google-style Python files in a directory.

    Scenario: Create two Python files with Google-style docstrings and convert the directory to Sphinx.
    Boundaries: Two files, dry_run=True; all files processed and changed.
    On failure, first check: convert_project file discovery logic and files_processed/files_changed counts.
    """
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
