"""Tests for style detector."""
from pydocstring.detector import detect_style
from pydocstring.models import DocstringStyle


def test_detect_empty():
    """Test that an empty string returns UNKNOWN style."""
    result = detect_style("")
    assert result.style == DocstringStyle.UNKNOWN


def test_detect_google_args():
    """Test detecting Google-style docstrings with Args section."""
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
    """Test detecting Sphinx-style docstrings with :param fields."""
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
    """Test detecting mixed-style docstrings."""
    text = """Do something.

Args:
    x (int): A number.

:returns: True if successful.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.MIXED


def test_detect_no_markers():
    """Test that a plain summary without markers returns UNKNOWN."""
    text = "Simple one-line docstring."
    result = detect_style(text)
    assert result.style == DocstringStyle.UNKNOWN


def test_detect_google_raises():
    """Test detecting Google-style docstrings with Raises section."""
    text = """Do something.

Raises:
    ValueError: If value is wrong.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.GOOGLE
