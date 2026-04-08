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
    result = rewrite_source(GOOGLE_SOURCE, target_style=DocstringStyle.SPHINX)
    assert ":param x:" in result
    assert ":type x: int" in result
    assert ":returns:" in result
    assert ":rtype: bool" in result
    assert ":raises ValueError:" in result
    assert "Args:" not in result


def test_sphinx_to_google():
    result = rewrite_source(SPHINX_SOURCE, target_style=DocstringStyle.GOOGLE)
    assert "Args:" in result
    assert "    x (int):" in result
    assert "Returns:" in result
    assert "    bool:" in result
    assert "Raises:" in result
    assert ":param" not in result


def test_no_change_same_style_google():
    result = rewrite_source(GOOGLE_SOURCE, target_style=DocstringStyle.GOOGLE)
    assert result == GOOGLE_SOURCE


def test_no_change_same_style_sphinx():
    result = rewrite_source(SPHINX_SOURCE, target_style=DocstringStyle.SPHINX)
    assert result == SPHINX_SOURCE


def test_rewrite_class_docstring():
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
    source = '''def foo():
    pass
'''
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    assert result == source


def test_rewrite_summary_only():
    source = '''def foo():
    """Simple summary."""
    pass
'''
    result = rewrite_source(source, target_style=DocstringStyle.SPHINX)
    # Should not crash and should preserve summary
    assert "Simple summary." in result


def test_explicit_source_style():
    result = rewrite_source(
        GOOGLE_SOURCE,
        target_style=DocstringStyle.SPHINX,
        source_style=DocstringStyle.GOOGLE,
    )
    assert ":param x:" in result
