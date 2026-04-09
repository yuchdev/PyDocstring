"""Tests for normalize module."""
from pydocstring.normalize import (
    detect_indent, detect_newline, strip_docstring_quotes, wrap_docstring_quotes,
)


def test_detect_indent_4_spaces():
    text = "def foo():\n    pass\n    return 1"
    assert detect_indent(text) == "    "


def test_detect_indent_2_spaces():
    text = "def foo():\n  pass\n  return 1"
    assert detect_indent(text) == "  "


def test_detect_indent_no_indent():
    text = "hello\nworld"
    assert detect_indent(text) == "    "


def test_detect_newline_lf():
    assert detect_newline("hello\nworld") == "\n"


def test_detect_newline_crlf():
    assert detect_newline("hello\r\nworld") == "\r\n"


def test_strip_docstring_quotes_double():
    assert strip_docstring_quotes('"""hello"""') == "hello"


def test_strip_docstring_quotes_single():
    assert strip_docstring_quotes("'''hello'''") == "hello"


def test_wrap_docstring_quotes():
    assert wrap_docstring_quotes("hello") == '"""hello"""'
    assert wrap_docstring_quotes("hello", "'''") == "'''hello'''"
