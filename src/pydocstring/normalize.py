"""Indentation and whitespace normalization helpers."""

from __future__ import annotations


def detect_indent(text: str) -> str:
    """Detect the dominant indent unit (4 spaces, 2 spaces, tab)."""
    lines = text.split("\n")
    indent_counts: dict[str, int] = {}
    for line in lines:
        if line and line[0] in (" ", "\t"):
            stripped = line.lstrip()
            if stripped:
                indent = line[: len(line) - len(stripped)]
                indent_counts[indent] = indent_counts.get(indent, 0) + 1
    if not indent_counts:
        return "    "
    dominant = max(indent_counts, key=indent_counts.__getitem__)
    return dominant


def normalize_indent(text: str, indent: str = "    ") -> str:
    """Normalize indentation."""
    lines = text.split("\n")
    result = []
    for line in lines:
        if not line.strip():
            result.append("")
        else:
            stripped = line.lstrip()
            current_indent = line[: len(line) - len(stripped)]
            level = len(current_indent) // max(1, len(detect_indent(text)))
            result.append(indent * level + stripped)
    return "\n".join(result)


def detect_newline(source: str) -> str:
    """Detect CRLF vs LF."""
    if "\r\n" in source:
        return "\r\n"
    return "\n"


def strip_docstring_quotes(docstring_node_value: str) -> str:
    """Strip triple-quote wrapping from a string literal value, return the inner text."""
    s = docstring_node_value
    for prefix in ('r"""', "r'''", 'u"""', "u'''", '"""', "'''"):
        if s.startswith(prefix):
            quote = prefix[-3:]
            if s.endswith(quote):
                return s[len(prefix) : -3]
    return s


def wrap_docstring_quotes(text: str, quote_char: str = '"""') -> str:
    """Wrap text in triple quotes."""
    return f"{quote_char}{text}{quote_char}"
