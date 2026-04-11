from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Optional


# ---------------------------------------------------------------------------
# Core Linter Pytest Wiring
# ---------------------------------------------------------------------------
@dataclass
class RuleViolation:
    pass


def check_tree(tree: ast.AST, filename: str, source: Optional[str] = None) -> Iterable[RuleViolation]:
    """Run all custom checks on a parsed AST."""
    pass

def check_file(path: Path) -> List[RuleViolation]:
    """
    Run all custom lint rules on a Python file and return violations.

    Reads the file, parses its AST, and applies all custom checks including
    broad exception handling, muted exceptions, Settings.set() usage,
    local imports, docstring requirements, and return type annotations.
    """
    pass


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _contains_exception(exc_node: ast.expr) -> bool:
    """Return True if the except type contains `Exception`."""
    pass


def _is_muting_stmt(stmt: ast.stmt) -> bool:
    """
    Return True if a statement is considered "muting" in an except block.

    Currently treated as muting:
        - pass
        - continue
        - break
        - return <anything>
        - a bare ellipsis expression: `...`
          (common "TODO" / placeholder pattern)
    """
    pass


def _has_proper_docstring(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, lines: Optional[Sequence[str]]) -> bool:
    """
    Check that `node` has a docstring as its first statement and that the
    corresponding source line begins with triple double quotes after
    indentation.
    """
    pass


def _is_test_module(tree: ast.AST, filename: str) -> bool:
    """
    Heuristically determine whether this module is a test module.

    Criteria:
        - File name starts with `test_` or ends with `_test.py`, OR
        - Any parent directory is named `tests`, OR
        - Module imports `pytest` or `unittest`.
    """
    pass


def _has_test_imports(tree: ast.AST) -> bool:
    """Return True if module imports pytest or unittest."""
    pass


def _iter_test_functions(tree: ast.AST) -> Iterable[ast.AST]:
    """
    Yield test case functions/methods:

    - Top-level `def test_*` (pytest-style)
    - Methods `def test_*` on classes whose name starts with `Test`
      or which inherit from `unittest.TestCase`.
    """
    pass


def _is_test_class(node: ast.ClassDef) -> bool:
    """Heuristic: pytest test class or unittest.TestCase subclass."""
    pass


def _docstring_has_structured_header(doc: str) -> bool:
    """Check first non-empty docstring line matches `[Type] summary` pattern with Type in {Unit, Integration, Mock, E2E}.

    Only accept [Unit], [Integration], [Mock], or [E2E] headers for test docstrings.
    """
    pass


def _docstring_has_section(doc: str, section_name: str) -> bool:
    """Return True if any line starts with the given section name."""
    pass


def _function_returns_value(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Return True if this function/method has at least one `return` that
    returns a value (i.e. `return <expr>` rather than bare `return`).

    NOTE: Does NOT inspect nested inner functions/lambdas/classes.
    """
    pass


def _except_catches_import_error(handler: ast.ExceptHandler) -> bool:
    """Return True if this except handler catches ImportError / ModuleNotFoundError."""
    pass


def _except_handler_has_raise(handler: ast.ExceptHandler) -> bool:
    """
    Return True if the except block contains any `raise` statement.

    We treat any raise in the handler body (even nested) as re-raising or
    propagating an error, so it's not considered suppression.
    """
    pass


def _is_union_with_none(ann: Optional[ast.expr]) -> bool:
    """
    Return True if the annotation contains a PEP 604-style union with None,
    e.g. `Foo | None`, `None | Foo`, or wider unions that include None.
    """
    pass


def _is_none_annotation(ann: Optional[ast.expr]) -> bool:
    """Return True if the given annotation node syntactically represents `None`.

    This is a compatibility wrapper kept for callers that expect an
    "annotation-focused" helper. The canonical implementation lives in
    `_expr_is_none`, which inspects AST nodes (including older AST node
    types) and returns True when they represent the literal `None`.
    """
    pass


def _expr_is_none(expr: Optional[ast.expr]) -> bool:
    """Return True if expr syntactically represents `None`."""
    pass

# ---------------------------------------------------------------------------
# Linter rules
# ---------------------------------------------------------------------------

def check_broad_exception(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """Rule 1: forbid broad `except Exception:` and bare `except:`."""
    pass


def check_settings_set_method(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """Rule 2: in class Settings, method `set` is forbidden."""
    pass


def check_muted_exception(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 3: forbid muted exception handlers.

    Any `except` block whose body consists only of "muting" statements:
        - pass
        - continue
        - break
        - return (with or without a value)
        - an ellipsis literal (`...`)
    is considered a violation (X004).
    """
    pass


def check_docstrings(tree: ast.AST, filename: str, source: Optional[str]) -> Iterable[RuleViolation]:
    """
    Rule 4 (unified X005):

    - If the module is a *code module*:
        Require a proper docstring as the first statement in every class /
        function / method body.

    - If the module is a *test module* (pytest/unittest or test_* heuristics):
        - For test functions/methods: require a structured test docstring with:
            * Header line: "[Type] component: behavior summary"
              where Type ∈ {Unit, Integration, Mock, E2E}
            * Sections: "Scenario:", "Boundaries:",
              "On failure, first check:"
        - For other functions/classes: require a generic docstring as above.
    """
    pass


def check_local_imports(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 5: forbid imports inside function bodies (local imports).

    Any `import ...` or `from ... import ...` statement that appears inside
    a function or method body is considered a violation (X006).
    """
    pass


def check_return_type_annotations(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 6 (X007):

    Every function or method that returns a value (has `return <expr>` in its
    own body) must declare an explicit return type annotation:

        def func(...) -> ReturnType:

    We don't validate *which* type, only that some annotation is present.
    """
    pass


def check_no_none_return_annotations(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 7 (X008):

    Never use an explicit `-> None` return annotation.

    Functions or methods that conceptually return nothing should omit a return
    annotation entirely instead of declaring `-> None`.
    """
    pass


def check_percent_formatting(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 8 (X009):

    Forbid old-style '%' string formatting such as:

        "%s %d" % (name, count)
        "%(name)s" % mapping

    and logging-style printf formatting such as:

        logger.info("Updated JSON %s", path)
        logger.debug("value=%d", value)

    Prefer f-strings instead, e.g.:

        logger.info(f"Updated JSON {path}")
    """
    pass


def check_import_error_suppression(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 9 (X010):

    Forbid suppressing ImportError / ModuleNotFoundError via try/except, e.g.:

        try:
            import foo
        except ImportError:
            foo = None

    Import failures must not be turned into optional dependencies or otherwise
    silently ignored. Let them propagate or handle them in a dedicated layer.
    """
    pass


def check_union_none_annotations(tree: ast.AST, filename: str,) -> Iterable[RuleViolation]:
    """
    Rule 10 (X011):

    Forbid use of `Type | None` (PEP 604 union syntax with `None`) in type
    hints and encourage `Optional[Type]` instead, e.g.:

        # forbidden
        def func(param: Foo | None) -> Bar | None: ...

        # preferred
        def func(param: Optional[Foo]) -> Optional[Bar]: ...
    """
    pass
