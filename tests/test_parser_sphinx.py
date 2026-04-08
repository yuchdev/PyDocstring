"""Tests for Sphinx-style docstring parser."""
from pydocstring.parser_sphinx import parse_sphinx
from pydocstring.models import DocstringStyle


def test_parse_empty():
    doc = parse_sphinx("")
    assert doc.summary == ""
    assert doc.params == []


def test_parse_summary_only():
    doc = parse_sphinx("Do something.")
    assert doc.summary == "Do something."


def test_parse_params():
    text = """Do something.

:param x: A number.
:type x: int
:param y: A string.
:type y: str
"""
    doc = parse_sphinx(text)
    assert len(doc.params) == 2
    assert doc.params[0].name == "x"
    assert doc.params[0].type_annotation == "int"
    assert doc.params[0].description == "A number."
    assert doc.params[1].name == "y"
    assert doc.params[1].type_annotation == "str"


def test_parse_returns():
    text = """Do something.

:returns: True if successful.
:rtype: bool
"""
    doc = parse_sphinx(text)
    assert doc.returns is not None
    assert doc.returns.type_annotation == "bool"
    assert doc.returns.description == "True if successful."


def test_parse_raises():
    text = """Do something.

:raises ValueError: If value is wrong.
:raises TypeError: If type is wrong.
"""
    doc = parse_sphinx(text)
    assert len(doc.raises) == 2
    assert doc.raises[0].exc_type == "ValueError"
    assert doc.raises[0].description == "If value is wrong."


def test_parse_yields():
    text = """Generate values.

:yields: A number.
"""
    doc = parse_sphinx(text)
    assert doc.yields is not None
    assert doc.yields.description == "A number."


def test_parse_param_inline_type():
    text = """Do something.

:param int x: A number.
"""
    doc = parse_sphinx(text)
    assert doc.params[0].name == "x"
    assert doc.params[0].type_annotation == "int"
