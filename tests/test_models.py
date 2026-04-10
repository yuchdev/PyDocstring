"""Tests for data models."""
from pydocstring.models import (
    DocstringStyle, ParamDoc, RaisesDoc, ReturnsDoc, YieldsDoc,
    SectionDoc, ParsedDocstring, StyleDetectionResult,
)


def test_docstring_style_values():
    """Test that DocstringStyle enum has the expected string values."""
    assert DocstringStyle.GOOGLE == "google"
    assert DocstringStyle.SPHINX == "sphinx"
    assert DocstringStyle.MIXED == "mixed"
    assert DocstringStyle.UNKNOWN == "unknown"


def test_param_doc():
    """Test that ParamDoc stores name, type and description correctly."""
    p = ParamDoc(name="x", type_annotation="int", description="A number")
    assert p.name == "x"
    assert p.type_annotation == "int"
    assert p.description == "A number"


def test_parsed_docstring_defaults():
    """Test that ParsedDocstring has sensible default values."""
    doc = ParsedDocstring()
    assert doc.summary == ""
    assert doc.params == []
    assert doc.returns is None
    assert doc.raises == []
