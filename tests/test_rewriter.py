"""Tests for the CST-based rewriter."""

from pydocstring.rewriter import rewrite_source
from pydocstring.models import DocstringStyle


GOOGLE_SOURCE = '''def foo(x, y):
    """Do something.

    Args:
        x (int): A number.
        y (str): A string.

    Returns:
        bool: True if successful.

    Raises:
        ValueError: If value is wrong.
    """
    pass
'''

SPHINX_SOURCE = '''def foo(x, y):
    """Do something.

    :param x: A number.
    :type x: int
    :param y: A string.
    :type y: str
    :returns: True if successful.
    :rtype: bool
    :raises ValueError: If value is wrong.
    """
    pass
'''


def test_google_to_sphinx():
    """[Unit] rewriter: rewrite_source converts Google-style docstrings to Sphinx style.

    Scenario: Call rewrite_source with GOOGLE_SOURCE targeting SPHINX style.
    Boundaries: Function docstring with Args, Returns, Raises sections; all converted to Sphinx fields.
    On failure, first check: rewrite_source conversion logic and CST rewriter transformation.
    """
    result = rewrite_source(GOOGLE_SOURCE, target_style=DocstringStyle.SPHINX)
    assert ":param x:" in result
    assert ":type x: int" in result
    assert ":returns:" in result
    assert ":rtype: bool" in result
    assert ":raises ValueError:" in result
    assert "Args:" not in result


def test_sphinx_to_google():
    """[Unit] rewriter: rewrite_source converts Sphinx-style docstrings to Google style.

    Scenario: Call rewrite_source with SPHINX_SOURCE targeting GOOGLE style.
    Boundaries: Function docstring with :param, :type, :returns, :rtype, :raises fields.
    On failure, first check: rewrite_source conversion logic and CST rewriter for Sphinx-to-Google.
    """
    result = rewrite_source(SPHINX_SOURCE, target_style=DocstringStyle.GOOGLE)
    assert "Args:" in result
    assert "    x (int):" in result
    assert "Returns:" in result
    assert "    bool:" in result
    assert "Raises:" in result
    assert ":param" not in result


def test_no_change_same_style_google():
    """[Unit] rewriter: rewrite_source returns source unchanged when target style matches Google source.

    Scenario: Call rewrite_source with GOOGLE_SOURCE targeting GOOGLE style.
    Boundaries: Source already in target style; output must equal input exactly.
    On failure, first check: rewrite_source no-op behavior when source and target styles match.
    """
    result = rewrite_source(GOOGLE_SOURCE, target_style=DocstringStyle.GOOGLE)
    assert result == GOOGLE_SOURCE


def test_no_change_same_style_sphinx():
    """[Unit] rewriter: rewrite_source returns source unchanged when target style matches Sphinx source.

    Scenario: Call rewrite_source with SPHINX_SOURCE targeting SPHINX style.
    Boundaries: Source already in target style; output must equal input exactly.
    On failure, first check: rewrite_source no-op behavior when source and target styles match.
    """
    result = rewrite_source(SPHINX_SOURCE, target_style=DocstringStyle.SPHINX)
    assert result == SPHINX_SOURCE


def test_rewrite_class_docstring():
    """[Unit] rewriter: rewrite_source rewrites a class-level Google docstring to Sphinx style.

    Scenario: Call rewrite_source on a class with a Google-style Args docstring, targeting Sphinx.
    Boundaries: Single class with one Args param; :param field must appear, Args must not.
    On failure, first check: rewrite_source class docstring handling and CST node traversal.
    """
    source = '''class Foo:
    """A class.

    Args:
        x (int): A number.
    """
    pass
'''
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    assert ":param x:" in result
    assert "Args:" not in result


def test_rewrite_module_docstring():
    """[Unit] rewriter: rewrite_source rewrites a module-level Google docstring to Sphinx style.

    Scenario: Call rewrite_source on source with a module-level Google-style docstring, targeting Sphinx.
    Boundaries: Module docstring with Args section; :param field must appear in converted output.
    On failure, first check: rewrite_source module-level docstring detection and CST rewriting.
    """
    source = '''"""Module docstring.

Args:
    x (int): A number.
"""

def foo():
    pass
'''
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    assert ":param x:" in result


def test_rewrite_multiple_functions():
    """[Unit] rewriter: rewrite_source rewrites all function docstrings in a multi-function file.

    Scenario: Call rewrite_source on source with two Google-style functions, targeting Sphinx.
    Boundaries: Two functions each with one param; both must be converted to Sphinx style.
    On failure, first check: rewrite_source iteration over multiple function definitions in CST.
    """
    source = '''def foo(x):
    """Foo function.

    Args:
        x (int): A number.
    """
    pass


def bar(y):
    """Bar function.

    Args:
        y (str): A string.
    """
    pass
'''
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    assert result.count(":param") == 2


def test_rewrite_no_docstring():
    """[Unit] rewriter: rewrite_source leaves a function without a docstring unchanged.

    Scenario: Call rewrite_source on source with a function that has no docstring, targeting Sphinx.
    Boundaries: Single function with no docstring; output must equal input exactly.
    On failure, first check: rewrite_source no-op behavior for functions without docstrings.
    """
    source = """def foo():
    pass
"""
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    assert result == source


def test_rewrite_summary_only():
    """[Unit] rewriter: rewrite_source preserves a summary-only docstring when rewriting.

    Scenario: Call rewrite_source on a function with a summary-only docstring, targeting Sphinx.
    Boundaries: Single-line summary docstring with no sections; summary must be preserved in output.
    On failure, first check: rewrite_source handling of summary-only docstrings without modification.
    """
    source = '''def foo():
    """Simple summary."""
    pass
'''
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    # Should not crash and should preserve summary
    assert "Simple summary." in result


def test_explicit_source_style():
    """[Unit] rewriter: rewrite_source converts correctly when source style is explicitly specified.

    Scenario: Call rewrite_source with GOOGLE_SOURCE, target SPHINX, and explicit source_style=GOOGLE.
    Boundaries: Source style explicitly provided; should produce same result as auto-detection.
    On failure, first check: rewrite_source explicit source_style parameter handling.
    """
    result = rewrite_source(
        GOOGLE_SOURCE,
        target_style=DocstringStyle.SPHINX,
        source_style=DocstringStyle.GOOGLE,
    )
    assert ":param x:" in result
