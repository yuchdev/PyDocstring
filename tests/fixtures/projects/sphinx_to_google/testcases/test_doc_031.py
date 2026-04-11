# tests/tools/lint/test_docstring_ir_parsing.py

import pytest
from textwrap import dedent

from tools.lint.docstring_rewriter import DocstringStyle, docstring_to_ir


def _doc(s: str) -> str:
    """Normalize triple-quoted doc literals for tests."""
    pass


def make_expected(**overrides):
    """Base expected dict for DocstringIR, with selective overrides."""
    pass


def _assert_ir_matches(ir, expected: dict):
        pass


# ---------------------------------------------------------------------------
# Google-style cases (10)
# ---------------------------------------------------------------------------

GOOGLE_CASES = [
    # 1) Brief only
    (
        "google_brief_only",
        _doc(
            """
            Short summary.
            """
        ),
        make_expected(
            brief="Short summary.",
        ),
    ),
    # 2) Brief + multi-line description
    (
        "google_description",
        _doc(
            """
            Short summary.

            Longer description line one.
            Line two.
            """
        ),
        make_expected(
            brief="Short summary.",
            description="Longer description line one.\nLine two.",
        ),
    ),
    # 3) Args with types, Returns with type, Raises
    (
        "google_args_returns_raises",
        _doc(
            """
            Summary line.

            Args:
                a (int): first argument
                b (str): second argument

            Returns:
                bool: True on success.

            Raises:
                ValueError: if invalid.
            """
        ),
        make_expected(
            brief="Summary line.",
            params=["a", "b"],
            param_types=["int", "str"],
            param_docs={"a": "first argument", "b": "second argument"},
            returns="True on success.",
            rtype="bool",
            raises={"ValueError": "if invalid."},
        ),
    ),
    # 4) Args with param without type
    (
        "google_param_without_type",
        _doc(
            """
            Summary.

            Args:
                a: description only
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a"],
            param_types=[""],
            param_docs={"a": "description only"},
        ),
    ),
    # 5) Args with multi-line param description
    (
        "google_param_multiline_desc",
        _doc(
            """
            Summary.

            Args:
                a (int): first line
                    second line
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a"],
            param_types=["int"],
            param_docs={"a": "first line\nsecond line"},
        ),
    ),
    # 6) Returns section without type
    (
        "google_returns_no_type",
        _doc(
            """
            Summary.

            Returns:
                Description only.
            """
        ),
        make_expected(
            brief="Summary.",
            returns="Description only.",
        ),
    ),
    # 7) Returns section with type but no description
    (
        "google_returns_type_only",
        _doc(
            """
            Summary.

            Returns:
                bool:
            """
        ),
        make_expected(
            brief="Summary.",
            returns="",
            rtype="bool",
        ),
    ),
    # 8) Yields section with type and description
    (
        "google_yields_with_type",
        _doc(
            """
            Summary.

            Yields:
                int: numbers
            """
        ),
        make_expected(
            brief="Summary.",
            yields="numbers",
            yield_type="int",
        ),
    ),
    # 9) Raises section with multiple exceptions
    (
        "google_multiple_raises",
        _doc(
            """
            Summary.

            Raises:
                ValueError: first problem.
                KeyError: second problem.
            """
        ),
        make_expected(
            brief="Summary.",
            raises={
                "ValueError": "first problem.",
                "KeyError": "second problem.",
            },
        ),
    ),
    # 10) Using 'Parameters' and 'Exceptions' synonyms
    (
        "google_parameters_exceptions_synonyms",
        _doc(
            """
            Summary.

            Parameters:
                a (int): first

            Exceptions:
                RuntimeError: broken
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a"],
            param_types=["int"],
            param_docs={"a": "first"},
            raises={"RuntimeError": "broken"},
        ),
    ),
]


@pytest.mark.parametrize(
    "case_name, raw, expected",
    GOOGLE_CASES,
    ids=[c[0] for c in GOOGLE_CASES],
)
def test_docstring_to_ir_google_cases(case_name, raw, expected):
        pass


# ---------------------------------------------------------------------------
# Sphinx-style cases (10)
# ---------------------------------------------------------------------------

SPHINX_CASES = [
    # 1) Simple param with type
    (
        "sphinx_param_with_type",
        _doc(
            """
            Summary line.

            :param int a: value
            """
        ),
        make_expected(
            brief="Summary line.",
            description="",
            params=["a"],
            param_types=["int"],
            param_docs={"a": "value"},
        ),
    ),
    # 2) Two params, returns + rtype
    (
        "sphinx_params_returns_rtype",
        _doc(
            """
            Summary line.

            :param int a: first argument
            :param str b: second argument
            :returns: True on success.
            :rtype: bool
            """
        ),
        make_expected(
            brief="Summary line.",
            params=["a", "b"],
            param_types=["int", "str"],
            param_docs={"a": "first argument", "b": "second argument"},
            returns="True on success.",
            rtype="bool",
        ),
    ),
    # 3) Param without type
    (
        "sphinx_param_without_type",
        _doc(
            """
            Summary.

            :param a: desc only
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a"],
            param_types=[""],
            param_docs={"a": "desc only"},
        ),
    ),
    # 4) Param + type in separate directive
    (
        "sphinx_param_and_type",
        _doc(
            """
            Summary.

            :param a: with type separately
            :type a: int
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a"],
            param_types=["int"],
            param_docs={"a": "with type separately"},
        ),
    ),
    # 5) Multi-line param description
    (
        "sphinx_param_multiline_desc",
        _doc(
            """
            Summary.

            :param int a: first line
                second line
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a"],
            param_types=["int"],
            param_docs={"a": "first line\nsecond line"},
        ),
    ),
    # 6) Returns with multi-line description
    (
        "sphinx_returns_multiline",
        _doc(
            """
            Summary.

            :returns: first line
                second line
            """
        ),
        make_expected(
            brief="Summary.",
            returns="first line\nsecond line",
        ),
    ),
    # 7) Multiple raises
    (
        "sphinx_multiple_raises",
        _doc(
            """
            Summary.

            :raises ValueError: first
            :raises KeyError: second
            """
        ),
        make_expected(
            brief="Summary.",
            raises={
                "ValueError": "first",
                "KeyError": "second",
            },
        ),
    ),
    # 8) Raise with multi-line description
    (
        "sphinx_raise_multiline",
        _doc(
            """
            Summary.

            :raises ValueError: first line
                second line
            """
        ),
        make_expected(
            brief="Summary.",
            raises={"ValueError": "first line\nsecond line"},
        ),
    ),
    # 9) Multi-line description before params
    (
        "sphinx_description_before_params",
        _doc(
            """
            Summary.

            Long description line one.
            Second line.

            :param int a: with param
            """
        ),
        make_expected(
            brief="Summary.",
            description="Long description line one.\nSecond line.",
            params=["a"],
            param_types=["int"],
            param_docs={"a": "with param"},
        ),
    ),
    # 10) Mixed typed/untyped params + separate :type + returns + rtype
    (
        "sphinx_mixed_params_returns",
        _doc(
            """
            Summary.

            :param int a: typed
            :param b: no type yet
            :type b: str
            :returns: ok
            :rtype: bool
            """
        ),
        make_expected(
            brief="Summary.",
            params=["a", "b"],
            param_types=["int", "str"],
            param_docs={"a": "typed", "b": "no type yet"},
            returns="ok",
            rtype="bool",
        ),
    ),
]


@pytest.mark.parametrize(
    "case_name, raw, expected",
    SPHINX_CASES,
    ids=[c[0] for c in SPHINX_CASES],
)
def test_docstring_to_ir_sphinx_cases(case_name, raw, expected):
        pass
