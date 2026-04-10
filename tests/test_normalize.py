"""Tests for normalize module."""

from pydocstring.normalize import (
    detect_indent,
    detect_newline,
    strip_docstring_quotes,
    wrap_docstring_quotes,
)


def test_detect_indent_4_spaces():
    """[Unit] normalize: detect_indent returns 4-space indentation for 4-space indented text.

    Scenario: Pass a multi-line string with 4-space indentation to detect_indent.
    Boundaries: Consistent 4-space indentation; no tabs or mixed indentation.
    On failure, first check: detect_indent regex or heuristic for identifying indent width.
    """
    text = "def foo():\n    pass\n    return 1"
    assert detect_indent(text) == "    "


def test_detect_indent_2_spaces():
    """[Unit] normalize: detect_indent returns 2-space indentation for 2-space indented text.

    Scenario: Pass a multi-line string with 2-space indentation to detect_indent.
    Boundaries: Consistent 2-space indentation; minimum non-zero indentation.
    On failure, first check: detect_indent minimum indentation detection logic.
    """
    text = "def foo():\n  pass\n  return 1"
    assert detect_indent(text) == "  "


def test_detect_indent_no_indent():
    """[Unit] normalize: detect_indent returns default 4-space indent when no indentation is found.

    Scenario: Pass a multi-line string with no indentation to detect_indent.
    Boundaries: All lines at column 0; default fallback indent is 4 spaces.
    On failure, first check: detect_indent fallback/default value logic.
    """
    text = "hello\nworld"
    assert detect_indent(text) == "    "


def test_detect_newline_lf():
    """[Unit] normalize: detect_newline returns LF for text with Unix line endings.

    Scenario: Call detect_newline with a string containing LF (\\n) line endings.
    Boundaries: String with a single LF newline; no CRLF present.
    On failure, first check: detect_newline LF detection and return value.
    """
    assert detect_newline("hello\nworld") == "\n"


def test_detect_newline_crlf():
    """[Unit] normalize: detect_newline returns CRLF for text with Windows line endings.

    Scenario: Call detect_newline with a string containing CRLF (\\r\\n) line endings.
    Boundaries: String with a single CRLF newline; CRLF takes priority over LF.
    On failure, first check: detect_newline CRLF detection order and return value.
    """
    assert detect_newline("hello\r\nworld") == "\r\n"


def test_strip_docstring_quotes_double():
    """[Unit] normalize: strip_docstring_quotes removes triple-double-quote delimiters.

    Scenario: Call strip_docstring_quotes with a triple-double-quoted string.
    Boundaries: Input wrapped in triple double quotes; inner content returned unchanged.
    On failure, first check: strip_docstring_quotes triple-double-quote stripping logic.
    """
    assert strip_docstring_quotes('"""hello"""') == "hello"


def test_strip_docstring_quotes_single():
    """[Unit] normalize: strip_docstring_quotes removes triple-single-quote delimiters.

    Scenario: Call strip_docstring_quotes with a triple-single-quoted string.
    Boundaries: Input wrapped in triple single quotes; inner content returned unchanged.
    On failure, first check: strip_docstring_quotes triple-single-quote stripping logic.
    """
    assert strip_docstring_quotes("'''hello'''") == "hello"


def test_wrap_docstring_quotes():
    """[Unit] normalize: wrap_docstring_quotes wraps text in triple-quote delimiters.

    Scenario: Call wrap_docstring_quotes with plain text and verify triple-double and triple-single quoting.
    Boundaries: Simple string input; both default (double) and explicit single-quote wrapping tested.
    On failure, first check: wrap_docstring_quotes quote delimiter selection and wrapping logic.
    """
    assert wrap_docstring_quotes("hello") == '"""hello"""'
    assert wrap_docstring_quotes("hello", "'''") == "'''hello'''"
