"""Tests for Sphinx-style docstring parser."""

from pydocstring.parser_sphinx import parse_sphinx


def test_parse_empty():
    """[Unit] parser_sphinx: parse_sphinx returns empty ParsedDocstring for an empty string.

    Scenario: Call parse_sphinx with an empty string.
    Boundaries: Empty string input; summary is empty, params list is empty.
    On failure, first check: parse_sphinx empty input handling and ParsedDocstring defaults.
    """
    doc = parse_sphinx("")
    assert doc.summary == ""
    assert doc.params == []


def test_parse_summary_only():
    """[Unit] parser_sphinx: parse_sphinx parses a single-line summary with no field directives.

    Scenario: Call parse_sphinx with a single-line docstring containing only a summary.
    Boundaries: Single line, no :param or :type fields; summary extracted correctly.
    On failure, first check: parse_sphinx summary extraction logic for single-line input.
    """
    doc = parse_sphinx("Do something.")
    assert doc.summary == "Do something."


def test_parse_params():
    """[Unit] parser_sphinx: parse_sphinx parses :param and :type fields into ParamDoc entries.

    Scenario: Call parse_sphinx with a docstring containing two :param and :type field pairs.
    Boundaries: Two parameters with names, type annotations, and descriptions; no return or raises fields.
    On failure, first check: parse_sphinx :param/:type field parsing and ParamDoc population logic.
    """
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
    """[Unit] parser_sphinx: parse_sphinx parses :returns and :rtype fields into ReturnsDoc.

    Scenario: Call parse_sphinx with a docstring containing :returns and :rtype fields.
    Boundaries: Single return entry with type annotation and description; no params or raises.
    On failure, first check: parse_sphinx :returns/:rtype field parsing and ReturnsDoc population.
    """
    text = """Do something.

:returns: True if successful.
:rtype: bool
"""
    doc = parse_sphinx(text)
    assert doc.returns is not None
    assert doc.returns.type_annotation == "bool"
    assert doc.returns.description == "True if successful."


def test_parse_raises():
    """[Unit] parser_sphinx: parse_sphinx parses :raises fields into RaisesDoc entries.

    Scenario: Call parse_sphinx with a docstring containing two :raises fields.
    Boundaries: Two exception types with descriptions; no params or return.
    On failure, first check: parse_sphinx :raises field parsing and RaisesDoc list population.
    """
    text = """Do something.

:raises ValueError: If value is wrong.
:raises TypeError: If type is wrong.
"""
    doc = parse_sphinx(text)
    assert len(doc.raises) == 2
    assert doc.raises[0].exc_type == "ValueError"
    assert doc.raises[0].description == "If value is wrong."


def test_parse_yields():
    """[Unit] parser_sphinx: parse_sphinx parses a :yields field into YieldsDoc.

    Scenario: Call parse_sphinx with a docstring containing a :yields field.
    Boundaries: Single yields entry with description only; no type annotation.
    On failure, first check: parse_sphinx :yields field parsing and YieldsDoc population logic.
    """
    text = """Generate values.

:yields: A number.
"""
    doc = parse_sphinx(text)
    assert doc.yields is not None
    assert doc.yields.description == "A number."


def test_parse_param_inline_type():
    """[Unit] parser_sphinx: parse_sphinx parses a :param field with inline type annotation.

    Scenario: Call parse_sphinx with a docstring that uses ':param int x:' inline type syntax.
    Boundaries: Single parameter with inline type; name and type_annotation must be correctly extracted.
    On failure, first check: parse_sphinx inline type extraction from ':param type name:' fields.
    """
    text = """Do something.

:param int x: A number.
"""
    doc = parse_sphinx(text)
    assert doc.params[0].name == "x"
    assert doc.params[0].type_annotation == "int"
