"""Tests for style detector."""
from pydocstring.detector import detect_style
from pydocstring.models import DocstringStyle


def test_detect_empty():
    """[Unit] detector: detect_style returns UNKNOWN for an empty string.

    Scenario: Call detect_style with an empty string and verify UNKNOWN style is returned.
    Boundaries: Empty string input; no style markers present.
    On failure, first check: detect_style default return value and DocstringStyle.UNKNOWN enum.
    """
    result = detect_style("")
    assert result.style == DocstringStyle.UNKNOWN


def test_detect_google_args():
    """[Unit] detector: detect_style returns GOOGLE for text with Args section.

    Scenario: Call detect_style with a multi-line docstring containing 'Args:' and 'Returns:' sections.
    Boundaries: Text has both summary and Google-style section markers; confidence > 0.5.
    On failure, first check: Google marker detection logic and confidence scoring in detect_style.
    """
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
    """[Unit] detector: detect_style returns SPHINX for text with :param and :rtype fields.

    Scenario: Call detect_style with a docstring containing ':param', ':type', ':returns:', ':rtype:' fields.
    Boundaries: Text has Sphinx-style field markers only; confidence > 0.5.
    On failure, first check: Sphinx marker detection logic and confidence scoring in detect_style.
    """
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
    """[Unit] detector: detect_style returns MIXED for text with both Google and Sphinx markers.

    Scenario: Call detect_style with a docstring that has both 'Args:' and ':returns:' markers.
    Boundaries: Text mixes Google and Sphinx markers; result style is MIXED.
    On failure, first check: mixed style detection logic and DocstringStyle.MIXED enum value.
    """
    text = """Do something.

Args:
    x (int): A number.

:returns: True if successful.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.MIXED


def test_detect_no_markers():
    """[Unit] detector: detect_style returns UNKNOWN for a plain summary without style markers.

    Scenario: Call detect_style with a single-line plain summary string.
    Boundaries: Text has no Google or Sphinx markers; result style is UNKNOWN.
    On failure, first check: fallback logic in detect_style when no markers are found.
    """
    text = "Simple one-line docstring."
    result = detect_style(text)
    assert result.style == DocstringStyle.UNKNOWN


def test_detect_google_raises():
    """[Unit] detector: detect_style returns GOOGLE for text with a Raises section.

    Scenario: Call detect_style with a docstring containing a 'Raises:' section.
    Boundaries: Text has a single Google-style Raises marker; result style is GOOGLE.
    On failure, first check: Google Raises section detection logic in detect_style.
    """
    text = """Do something.

Raises:
    ValueError: If value is wrong.
"""
    result = detect_style(text)
    assert result.style == DocstringStyle.GOOGLE
