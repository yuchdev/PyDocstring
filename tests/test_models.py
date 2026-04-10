"""Tests for data models."""

from pydocstring.models import (
    DocstringStyle,
    ParamDoc,
    ParsedDocstring,
)


def test_docstring_style_values():
    """[Unit] models: DocstringStyle enum has the expected string values.

    Scenario: Access GOOGLE, SPHINX, MIXED, and UNKNOWN enum members and compare their values.
    Boundaries: All four standard styles covered; values are lowercase strings.
    On failure, first check: DocstringStyle enum definitions and their assigned string values.
    """
    assert DocstringStyle.GOOGLE == "google"
    assert DocstringStyle.SPHINX == "sphinx"
    assert DocstringStyle.MIXED == "mixed"
    assert DocstringStyle.UNKNOWN == "unknown"


def test_param_doc():
    """[Unit] models: ParamDoc stores name, type annotation, and description correctly.

    Scenario: Construct a ParamDoc with name, type_annotation, and description and verify attributes.
    Boundaries: Simple string values for all fields; no optional fields omitted.
    On failure, first check: ParamDoc dataclass field definitions and constructor behavior.
    """
    p = ParamDoc(name="x", type_annotation="int", description="A number")
    assert p.name == "x"
    assert p.type_annotation == "int"
    assert p.description == "A number"


def test_parsed_docstring_defaults():
    """[Unit] models: ParsedDocstring has sensible default values when constructed with no arguments.

    Scenario: Construct a ParsedDocstring with no arguments and verify default attribute values.
    Boundaries: No arguments passed; expects empty summary, empty params list, None returns, empty raises.
    On failure, first check: ParsedDocstring dataclass default values for all fields.
    """
    doc = ParsedDocstring()
    assert doc.summary == ""
    assert doc.params == []
    assert doc.returns is None
    assert doc.raises == []
