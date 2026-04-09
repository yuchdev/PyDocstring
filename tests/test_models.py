"""Tests for data models."""
from pydocstring.models import (
    DocstringStyle, ParamDoc, RaisesDoc, ReturnsDoc, YieldsDoc,
    SectionDoc, ParsedDocstring, StyleDetectionResult,
)


def test_docstring_style_values():
    assert DocstringStyle.GOOGLE == "google"
    assert DocstringStyle.SPHINX == "sphinx"
    assert DocstringStyle.MIXED == "mixed"
    assert DocstringStyle.UNKNOWN == "unknown"


def test_param_doc():
    p = ParamDoc(name="x", type_annotation="int", description="A number")
    assert p.name == "x"
    assert p.type_annotation == "int"
    assert p.description == "A number"


def test_parsed_docstring_defaults():
    doc = ParsedDocstring()
    assert doc.summary == ""
    assert doc.params == []
    assert doc.returns is None
    assert doc.raises == []
