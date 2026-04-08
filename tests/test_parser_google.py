"""Tests for Google-style docstring parser."""
from pydocstring.parser_google import parse_google
from pydocstring.models import DocstringStyle


def test_parse_empty():
    doc = parse_google("")
    assert doc.summary == ""
    assert doc.params == []


def test_parse_summary_only():
    doc = parse_google("Do something.")
    assert doc.summary == "Do something."
    assert doc.params == []
    assert doc.returns is None


def test_parse_summary_and_extended():
    text = """Do something.

This is a longer description
that spans multiple lines.
"""
    doc = parse_google(text)
    assert doc.summary == "Do something."
    assert "longer description" in doc.extended_description


def test_parse_args():
    text = """Do something.

Args:
    x (int): A number.
    y (str): A string.
"""
    doc = parse_google(text)
    assert len(doc.params) == 2
    assert doc.params[0].name == "x"
    assert doc.params[0].type_annotation == "int"
    assert doc.params[0].description == "A number."
    assert doc.params[1].name == "y"
    assert doc.params[1].type_annotation == "str"


def test_parse_returns():
    text = """Do something.

Returns:
    bool: True if successful.
"""
    doc = parse_google(text)
    assert doc.returns is not None
    assert doc.returns.type_annotation == "bool"
    assert doc.returns.description == "True if successful."


def test_parse_yields():
    text = """Generate values.

Yields:
    int: A number.
"""
    doc = parse_google(text)
    assert doc.yields is not None
    assert doc.yields.type_annotation == "int"


def test_parse_raises():
    text = """Do something.

Raises:
    ValueError: If value is wrong.
    TypeError: If type is wrong.
"""
    doc = parse_google(text)
    assert len(doc.raises) == 2
    assert doc.raises[0].exc_type == "ValueError"
    assert doc.raises[0].description == "If value is wrong."
    assert doc.raises[1].exc_type == "TypeError"


def test_parse_custom_section():
    text = """Do something.

Examples:
    >>> foo(1)
    2
"""
    doc = parse_google(text)
    assert len(doc.custom_sections) == 1
    assert doc.custom_sections[0].title == "Examples"


def test_parse_args_no_type():
    text = """Do something.

Args:
    x: A number.
"""
    doc = parse_google(text)
    assert doc.params[0].name == "x"
    assert doc.params[0].type_annotation is None
    assert doc.params[0].description == "A number."


def test_parse_indented_docstring():
    text = """    Do something.

    Args:
        x (int): A number.

    Returns:
        bool: True if successful.
    """
    doc = parse_google(text)
    assert doc.summary == "Do something."
    assert len(doc.params) == 1
    assert doc.returns is not None


def test_parse_returns_no_type():
    text = """Do something.

Returns:
    True if successful.
"""
    doc = parse_google(text)
    assert doc.returns is not None
    assert doc.returns.type_annotation is None
    assert "True if successful" in doc.returns.description
