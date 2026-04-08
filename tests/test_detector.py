"""Tests for style detector."""
from pydocstring.detector import detect_style
from pydocstring.models import DocstringStyle


def test_detect_empty():
    result = detect_style("")
    assert result.style == DocstringStyle.UNKNOWN


def test_detect_google_args():
    text = """Do something.

Args:
    x (int): A number.
    y (str): A string.

Returns:
    bool: True if successful.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.GOOGLE
    assert result.confidence > 0.5


def test_detect_sphinx():
    text = """Do something.

:param x: A number.
:type x: int
:returns: True if successful.
:rtype: bool
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.SPHINX
    assert result.confidence > 0.5


def test_detect_mixed():
    text = """Do something.

Args:
    x (int): A number.

:returns: True if successful.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.MIXED


def test_detect_no_markers():
    text = "Simple one-line docstring."
    result = detect_style(text)
    assert result.style == DocstringStyle.UNKNOWN


def test_detect_google_raises():
    text = """Do something.

Raises:
    ValueError: If value is wrong.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.GOOGLE
