"""Tests for Google and Sphinx renderers."""
from pydocstring.renderer_google import render_google
from pydocstring.renderer_sphinx import render_sphinx
from pydocstring.models import ParsedDocstring, ParamDoc, RaisesDoc, ReturnsDoc, YieldsDoc, SectionDoc


def make_doc() -> ParsedDocstring:
    """[Unit] renderers: build a sample ParsedDocstring fixture for renderer tests.

    Scenario: Construct a ParsedDocstring with params, returns, and raises for use in renderer tests.
    Boundaries: Two params (int, str), one returns (bool), one raises (ValueError).
    On failure, first check: ParsedDocstring, ParamDoc, ReturnsDoc, and RaisesDoc constructors.
    """
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
    """[Unit] renderers: render_google renders a summary-only ParsedDocstring correctly.

    Scenario: Call render_google with a ParsedDocstring containing only a summary line.
    Boundaries: Single summary string; no params, returns, or raises.
    On failure, first check: render_google summary-only rendering logic.
    """
    doc = ParsedDocstring(summary="Do something.")
    result = render_google(doc)
    assert result == "Do something."


def test_render_google_params():
    """[Unit] renderers: render_google renders the Args section with typed parameters.

    Scenario: Call render_google with a ParsedDocstring containing two typed parameters.
    Boundaries: Two params with name, type, and description; Args section must appear in output.
    On failure, first check: render_google Args section formatting logic.
    """
    doc = make_doc()
    result = render_google(doc)
    assert "Args:" in result
    assert "    x (int): A number." in result
    assert "    y (str): A string." in result


def test_render_google_returns():
    """[Unit] renderers: render_google renders the Returns section in Google style.

    Scenario: Call render_google with a ParsedDocstring containing a returns entry.
    Boundaries: Returns entry with type and description; Returns section must appear in output.
    On failure, first check: render_google Returns section formatting logic.
    """
    doc = make_doc()
    result = render_google(doc)
    assert "Returns:" in result
    assert "    bool: True if successful." in result


def test_render_google_raises():
    """[Unit] renderers: render_google renders the Raises section in Google style.

    Scenario: Call render_google with a ParsedDocstring containing a raises entry.
    Boundaries: Single raises entry with exception type and description; Raises section must appear.
    On failure, first check: render_google Raises section formatting logic.
    """
    doc = make_doc()
    result = render_google(doc)
    assert "Raises:" in result
    assert "    ValueError: If value is wrong." in result


def test_render_sphinx_params():
    """[Unit] renderers: render_sphinx renders :param and :type fields for typed parameters.

    Scenario: Call render_sphinx with a ParsedDocstring containing two typed parameters.
    Boundaries: Two params with name, type, and description; :param and :type fields must appear.
    On failure, first check: render_sphinx :param and :type field rendering logic.
    """
    doc = make_doc()
    result = render_sphinx(doc)
    assert ":param x: A number." in result
    assert ":type x: int" in result
    assert ":param y: A string." in result


def test_render_sphinx_returns():
    """[Unit] renderers: render_sphinx renders :returns and :rtype fields.

    Scenario: Call render_sphinx with a ParsedDocstring containing a returns entry with type.
    Boundaries: Returns entry with type annotation and description; :returns and :rtype must appear.
    On failure, first check: render_sphinx :returns and :rtype rendering logic.
    """
    doc = make_doc()
    result = render_sphinx(doc)
    assert ":returns: True if successful." in result
    assert ":rtype: bool" in result


def test_render_sphinx_raises():
    """[Unit] renderers: render_sphinx renders :raises fields for exception entries.

    Scenario: Call render_sphinx with a ParsedDocstring containing a raises entry.
    Boundaries: Single raises entry with exception type and description; :raises field must appear.
    On failure, first check: render_sphinx :raises field rendering logic.
    """
    doc = make_doc()
    result = render_sphinx(doc)
    assert ":raises ValueError: If value is wrong." in result


def test_render_google_no_type():
    """[Unit] renderers: render_google renders a param with no type annotation in Google style.

    Scenario: Call render_google with a param that has no type_annotation set.
    Boundaries: Single param without type; output uses 'x: description' format (no parentheses).
    On failure, first check: render_google param rendering logic for params without type annotations.
    """
    doc = ParsedDocstring(
        summary="Do something.",
        params=[ParamDoc(name="x", description="A number.")],
    )
    result = render_google(doc)
    assert "    x: A number." in result


def test_render_sphinx_no_type():
    """[Unit] renderers: render_sphinx renders a param with no type annotation without :type field.

    Scenario: Call render_sphinx with a param that has no type_annotation set.
    Boundaries: Single param without type; :param field appears but :type field must not appear.
    On failure, first check: render_sphinx conditional :type field rendering logic.
    """
    doc = ParsedDocstring(
        summary="Do something.",
        params=[ParamDoc(name="x", description="A number.")],
    )
    result = render_sphinx(doc)
    assert ":param x: A number." in result
    assert ":type x:" not in result


def test_render_google_extended_desc():
    """[Unit] renderers: render_google renders extended description after the summary line.

    Scenario: Call render_google with a ParsedDocstring containing both summary and extended_description.
    Boundaries: Summary and extended description present; both must appear in rendered output.
    On failure, first check: render_google extended description inclusion and ordering logic.
    """
    doc = ParsedDocstring(
        summary="Do something.",
        extended_description="More details here.",
    )
    result = render_google(doc)
    assert "Do something." in result
    assert "More details here." in result


def test_render_sphinx_no_blank_before_fields_when_no_summary():
    """[Unit] renderers: render_sphinx does not add a leading blank line when there is no summary.

    Scenario: Call render_sphinx with a ParsedDocstring that has no summary, only params.
    Boundaries: Empty summary; output must not start with a blank line.
    On failure, first check: render_sphinx leading blank line logic when summary is absent.
    """
    doc = ParsedDocstring(
        params=[ParamDoc(name="x", description="A number.")],
    )
    result = render_sphinx(doc)
    # Should not start with blank line
    assert not result.startswith('\n')


def test_render_google_yields():
    """[Unit] renderers: render_google renders the Yields section with type and description.

    Scenario: Call render_google with a ParsedDocstring containing a yields entry.
    Boundaries: Yields entry with type annotation and description; Yields section must appear.
    On failure, first check: render_google Yields section formatting logic.
    """
    doc = ParsedDocstring(
        summary="Generate values.",
        yields=YieldsDoc(type_annotation="int", description="A number."),
    )
    result = render_google(doc)
    assert "Yields:" in result
    assert "    int: A number." in result


def test_render_sphinx_yields():
    """[Unit] renderers: render_sphinx renders a :yields field with description.

    Scenario: Call render_sphinx with a ParsedDocstring containing a yields entry with description only.
    Boundaries: Yields entry with no type annotation; :yields field must appear in output.
    On failure, first check: render_sphinx :yields field rendering logic.
    """
    doc = ParsedDocstring(
        summary="Generate values.",
        yields=YieldsDoc(description="A number."),
    )
    result = render_sphinx(doc)
    assert ":yields: A number." in result


def test_render_google_custom_section():
    """[Unit] renderers: render_google renders a custom section (e.g. Examples) in Google style.

    Scenario: Call render_google with a ParsedDocstring containing a custom 'Examples' section.
    Boundaries: Single custom section with title and content; Examples header must appear in output.
    On failure, first check: render_google custom section formatting logic.
    """
    doc = ParsedDocstring(
        summary="Do something.",
        custom_sections=[SectionDoc(title="Examples", content=">>> foo(1)\n2")],
    )
    result = render_google(doc)
    assert "Examples:" in result
    assert "    >>> foo(1)" in result


def test_render_sphinx_custom_section():
    """[Unit] renderers: render_sphinx renders a custom section (e.g. Examples) in Sphinx style.

    Scenario: Call render_sphinx with a ParsedDocstring containing a custom 'Examples' section.
    Boundaries: Single custom section with title and content; Examples header must appear in output.
    On failure, first check: render_sphinx custom section formatting logic.
    """
    doc = ParsedDocstring(
        summary="Do something.",
        custom_sections=[SectionDoc(title="Examples", content=">>> foo(1)\n2")],
    )
    result = render_sphinx(doc)
    assert "Examples:" in result
