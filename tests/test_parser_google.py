"""Tests for Google-style docstring parser."""

from pydocstring.parser_google import parse_google


def test_parse_empty():
    """[Unit] parser_google: parse_google returns empty ParsedDocstring for an empty string.

    Scenario: Call parse_google with an empty string.
    Boundaries: Empty string input; summary is empty, params list is empty.
    On failure, first check: parse_google empty input handling and ParsedDocstring defaults.
    """
    doc = parse_google("")
    assert doc.summary == ""
    assert doc.params == []


def test_parse_summary_only():
    """[Unit] parser_google: parse_google parses a single-line summary with no sections.

    Scenario: Call parse_google with a single-line docstring containing only a summary.
    Boundaries: Single line, no Args/Returns/Raises sections; params list is empty, returns is None.
    On failure, first check: parse_google summary extraction logic.
    """
    doc = parse_google("Do something.")
    assert doc.summary == "Do something."
    assert doc.params == []
    assert doc.returns is None


def test_parse_summary_and_extended():
    """[Unit] parser_google: parse_google parses summary and extended description sections.

    Scenario: Call parse_google with a docstring that has a summary and a multi-line extended description.
    Boundaries: Summary and extended description separated by a blank line; no Args or Returns.
    On failure, first check: parse_google extended description extraction and blank-line separation logic.
    """
    text = """Do something.

This is a longer description
that spans multiple lines.
"""
    doc = parse_google(text)
    assert doc.summary == "Do something."
    assert "longer description" in doc.extended_description


def test_parse_args():
    """[Unit] parser_google: parse_google parses Args section with typed parameters.

    Scenario: Call parse_google with a docstring that has an Args section with two typed parameters.
    Boundaries: Two parameters, both with type annotations and descriptions; summary present.
    On failure, first check: parse_google Args section parsing and ParamDoc population logic.
    """
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
    """[Unit] parser_google: parse_google parses a Returns section with type and description.

    Scenario: Call parse_google with a docstring that has a Returns section.
    Boundaries: Single return with type annotation and description; no params.
    On failure, first check: parse_google Returns section parsing and ReturnsDoc population logic.
    """
    text = """Do something.

Returns:
    bool: True if successful.
"""
    doc = parse_google(text)
    assert doc.returns is not None
    assert doc.returns.type_annotation == "bool"
    assert doc.returns.description == "True if successful."


def test_parse_yields():
    """[Unit] parser_google: parse_google parses a Yields section with type annotation.

    Scenario: Call parse_google with a docstring that has a Yields section.
    Boundaries: Single yield entry with type annotation; no params or returns.
    On failure, first check: parse_google Yields section parsing and YieldsDoc population logic.
    """
    text = """Generate values.

Yields:
    int: A number.
"""
    doc = parse_google(text)
    assert doc.yields is not None
    assert doc.yields.type_annotation == "int"


def test_parse_raises():
    """[Unit] parser_google: parse_google parses a Raises section with multiple exception entries.

    Scenario: Call parse_google with a docstring that has a Raises section listing two exceptions.
    Boundaries: Two exception types with descriptions; no params or returns.
    On failure, first check: parse_google Raises section parsing and RaisesDoc list population.
    """
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
    """[Unit] parser_google: parse_google parses a custom Examples section.

    Scenario: Call parse_google with a docstring that has an Examples section.
    Boundaries: Single custom section; title is 'Examples'; no standard sections present.
    On failure, first check: parse_google custom section detection and SectionDoc population.
    """
    text = """Do something.

Examples:
    >>> foo(1)
    2
"""
    doc = parse_google(text)
    assert len(doc.custom_sections) == 1
    assert doc.custom_sections[0].title == "Examples"


def test_parse_args_no_type():
    """[Unit] parser_google: parse_google parses an Args section with untyped parameters.

    Scenario: Call parse_google with a docstring that has an Args section where params have no type.
    Boundaries: Single parameter without type annotation; type_annotation should be None.
    On failure, first check: parse_google param parsing logic for entries without type brackets.
    """
    text = """Do something.

Args:
    x: A number.
"""
    doc = parse_google(text)
    assert doc.params[0].name == "x"
    assert doc.params[0].type_annotation is None
    assert doc.params[0].description == "A number."


def test_parse_indented_docstring():
    """[Unit] parser_google: parse_google parses a docstring with leading indentation.

    Scenario: Call parse_google with a docstring that has 4-space indentation on all lines.
    Boundaries: Indented summary, Args, and Returns sections; indentation stripped correctly.
    On failure, first check: parse_google indentation stripping logic for function body docstrings.
    """
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
    """[Unit] parser_google: parse_google parses a Returns section with no type annotation.

    Scenario: Call parse_google with a docstring that has a Returns section without a type prefix.
    Boundaries: Returns content has no 'type:' prefix; type_annotation should be None.
    On failure, first check: parse_google Returns section handling for untyped return descriptions.
    """
    text = """Do something.

Returns:
    True if successful.
"""
    doc = parse_google(text)
    assert doc.returns is not None
    assert doc.returns.type_annotation is None
    assert "True if successful" in doc.returns.description
