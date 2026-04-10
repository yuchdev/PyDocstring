"""Tests for normalize module."""
from pydocstring.normalize import (
    detect_indent, detect_newline, strip_docstring_quotes, wrap_docstring_quotes,
)


def test_detect_indent_4_spaces():
    """Test that 4-space indentation is detected correctly."""
    text = "def foo():\n    pass\n    return 1"
    assert detect_indent(text) == "    "


def test_detect_indent_2_spaces():
    """Test that 2-space indentation is detected correctly."""
    text = "def foo():\n  pass\n  return 1"
    assert detect_indent(text) == "  "


def test_detect_indent_no_indent():
    """Test that the default indent is 4 spaces when no indentation is found."""
    text = "hello\nworld"
    assert detect_indent(text) == "    "


def test_detect_newline_lf():
    """Test that LF newlines are detected correctly."""
    assert detect_newline("hello\nworld") == "\n"


def test_detect_newline_crlf():
    """Test that CRLF newlines are detected correctly."""
    assert detect_newline("hello\r\nworld") == "\r\n"


def test_strip_docstring_quotes_double():
    """Test stripping double-quote docstring delimiters."""
    assert strip_docstring_quotes('"""hello"""') == "hello"


def test_strip_docstring_quotes_single():
    """Test stripping single-quote docstring delimiters."""
    assert strip_docstring_quotes("'''hello'''") == "hello"


def test_wrap_docstring_quotes():
    """Test wrapping text in docstring quote delimiters."""
    assert wrap_docstring_quotes("hello") == '"""hello"""'
    assert wrap_docstring_quotes("hello", "'''") == "'''hello'''"
