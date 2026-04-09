"""Tests for Google and Sphinx renderers."""
from pydocstring.renderer_google import render_google
from pydocstring.renderer_sphinx import render_sphinx
from pydocstring.models import ParsedDocstring, ParamDoc, RaisesDoc, ReturnsDoc, YieldsDoc, SectionDoc


def make_doc():
    return ParsedDocstring(
        summary="Do something.",
        params=[
            ParamDoc(name="x", type_annotation="int", description="A number."),
            ParamDoc(name="y", type_annotation="str", description="A string."),
        ],
        returns=ReturnsDoc(type_annotation="bool", description="True if successful."),
        raises=[RaisesDoc(exc_type="ValueError", description="If value is wrong.")],
    )


def test_render_google_summary():
    doc = ParsedDocstring(summary="Do something.")
    result = render_google(doc)
    assert result == "Do something."


def test_render_google_params():
    doc = make_doc()
    result = render_google(doc)
    assert "Args:" in result
    assert "    x (int): A number." in result
    assert "    y (str): A string." in result


def test_render_google_returns():
    doc = make_doc()
    result = render_google(doc)
    assert "Returns:" in result
    assert "    bool: True if successful." in result


def test_render_google_raises():
    doc = make_doc()
    result = render_google(doc)
    assert "Raises:" in result
    assert "    ValueError: If value is wrong." in result


def test_render_sphinx_params():
    doc = make_doc()
    result = render_sphinx(doc)
    assert ":param x: A number." in result
    assert ":type x: int" in result
    assert ":param y: A string." in result


def test_render_sphinx_returns():
    doc = make_doc()
    result = render_sphinx(doc)
    assert ":returns: True if successful." in result
    assert ":rtype: bool" in result


def test_render_sphinx_raises():
    doc = make_doc()
    result = render_sphinx(doc)
    assert ":raises ValueError: If value is wrong." in result


def test_render_google_no_type():
    doc = ParsedDocstring(
        summary="Do something.",
        params=[ParamDoc(name="x", description="A number.")],
    )
    result = render_google(doc)
    assert "    x: A number." in result


def test_render_sphinx_no_type():
    doc = ParsedDocstring(
        summary="Do something.",
        params=[ParamDoc(name="x", description="A number.")],
    )
    result = render_sphinx(doc)
    assert ":param x: A number." in result
    assert ":type x:" not in result


def test_render_google_extended_desc():
    doc = ParsedDocstring(
        summary="Do something.",
        extended_description="More details here.",
    )
    result = render_google(doc)
    assert "Do something." in result
    assert "More details here." in result


def test_render_sphinx_no_blank_before_fields_when_no_summary():
    doc = ParsedDocstring(
        params=[ParamDoc(name="x", description="A number.")],
    )
    result = render_sphinx(doc)
    # Should not start with blank line
    assert not result.startswith('\n')


def test_render_google_yields():
    doc = ParsedDocstring(
        summary="Generate values.",
        yields=YieldsDoc(type_annotation="int", description="A number."),
    )
    result = render_google(doc)
    assert "Yields:" in result
    assert "    int: A number." in result


def test_render_sphinx_yields():
    doc = ParsedDocstring(
        summary="Generate values.",
        yields=YieldsDoc(description="A number."),
    )
    result = render_sphinx(doc)
    assert ":yields: A number." in result


def test_render_google_custom_section():
    doc = ParsedDocstring(
        summary="Do something.",
        custom_sections=[SectionDoc(title="Examples", content=">>> foo(1)\n2")],
    )
    result = render_google(doc)
    assert "Examples:" in result
    assert "    >>> foo(1)" in result


def test_render_sphinx_custom_section():
    doc = ParsedDocstring(
        summary="Do something.",
        custom_sections=[SectionDoc(title="Examples", content=">>> foo(1)\n2")],
    )
    result = render_sphinx(doc)
    assert "Examples:" in result
