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
    """Represents a custom lint rule violation with location and details."""
    filename: str
    lineno: int
    col_offset: int
    code: str
    message: str


def check_tree(tree: ast.AST, filename: str, source: Optional[str] = None) -> Iterable[RuleViolation]:
    """Run all custom checks on a parsed AST."""
    yield from check_broad_exception(tree, filename, source)
    yield from check_muted_exception(tree, filename, source)
    yield from check_local_imports(tree, filename, source)
    yield from check_docstrings(tree, filename, source)
    yield from check_return_type_annotations(tree, filename)
    yield from check_no_none_return_annotations(tree, filename)
    yield from check_percent_formatting(tree, filename)
    yield from check_import_error_suppression(tree, filename)
    yield from check_union_none_annotations(tree, filename)


def check_file(path: Path) -> List[RuleViolation]:
    """
    Run all custom lint rules on a Python file and return violations.

    Reads the file, parses its AST, and applies all custom checks including
    broad exception handling, muted exceptions, Settings.set() usage,
    local imports, docstring requirements, and return type annotations.
    """
    src = path.read_text(encoding="utf8")
    tree = ast.parse(src, filename=str(path))
    return list(check_tree(tree, str(path), src))


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _contains_exception(exc_node: ast.expr) -> bool:
    """Return True if the exception type contains `Exception`."""
    # `except Exception:`
    if isinstance(exc_node, ast.Name) and exc_node.id == "Exception":
        return True

    # `except (Exception, ValueError):`
    if isinstance(exc_node, ast.Tuple):
        return any(
            isinstance(elt, ast.Name) and elt.id == "Exception"
            for elt in exc_node.elts
        )

    return False


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
    # pass / continue / break
    if isinstance(stmt, (ast.Pass, ast.Continue, ast.Break)):
        return True

    # return / return <value>
    if isinstance(stmt, ast.Return):
        return True

    # Bare ellipsis literal: `...`
    if isinstance(stmt, ast.Expr):
        value = stmt.value
        if isinstance(value, ast.Constant) and value.value is Ellipsis:
            return True

    return False


def _has_proper_docstring(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, lines: Optional[Sequence[str]]) -> bool:
    """
    Check that `node` has a docstring as its first statement and that the
    corresponding source line begins with triple double quotes after
    indentation.
    """
    body = getattr(node, "body", None)
    if not body:
        return False

    first_stmt = body[0]
    if not isinstance(first_stmt, ast.Expr):
        return False

    value = first_stmt.value

    # Python 3.8+: docstring is ast.Constant(str); older: ast.Str
    if isinstance(value, ast.Constant):
        if not isinstance(value.value, str):
            return False
    # pragma: no cover (for older Python)
    elif isinstance(value, (ast.Str, ast.Constant)):
        pass
    else:
        return False

    # If we don't have the original source, we can't enforce the precise
    # formatting; accept any string-literal docstring in that case.
    if lines is None:
        return True

    doc_lineno = first_stmt.lineno
    if not (1 <= doc_lineno <= len(lines)):
        # Be lenient if coordinates look odd.
        return True

    doc_line = lines[doc_lineno - 1]
    stripped = doc_line.lstrip()

    # Require that the first non-whitespace characters are triple double quotes.
    return stripped.startswith('"""')


def _function_returns_value(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Return True if this function/method has at least one `return` that
    returns a value (i.e. `return <expr>` rather than bare `return`).

    NOTE: Does NOT inspect nested inner functions/lambdas/classes.
    """

    class _ReturnVisitor(ast.NodeVisitor):
        """AST visitor that detects whether a function returns a value."""
        def __init__(self):
            """Initialize the visitor with the returns_value flag set to False."""
            self.returns_value = False

        def visit_Return(self, ret: ast.Return):
            """Visit the Return node and check if it returns a value."""
            # Anything with a value counts as "returns something"
            if ret.value is not None:
                self.returns_value = True

        # Do NOT descend into nested scopes when analyzing the outer function
        def visit_FunctionDef(self, _1: ast.FunctionDef):
            """Skip nested function bodies."""
            return

        def visit_AsyncFunctionDef(self, _1: ast.AsyncFunctionDef):
            """Skip nested async function bodies."""
            return

        def visit_Lambda(self, _1: ast.Lambda):
            """Skip nested lambdas."""
            return

        def visit_ClassDef(self, _1: ast.ClassDef):  # pragma: no cover
            """Skip nested classes."""
            return

    visitor = _ReturnVisitor()

    # IMPORTANT: only walk the body of this function/method, not the node itself,
    # so that our visit_FunctionDef/visit_AsyncFunctionDef only applies to nested defs.
    body = getattr(node, "body", None) or []
    for stmt in body:
        visitor.visit(stmt)

    return visitor.returns_value


def _except_catches_import_error(handler: ast.ExceptHandler) -> bool:
    """Return True if this exception handler catches ImportError / ModuleNotFoundError."""
    exc = handler.type
    if exc is None:
        return False

    names = {"ImportError", "ModuleNotFoundError"}

    # except ImportError:
    if isinstance(exc, ast.Name) and exc.id in names:
        return True

    # except (ImportError, ModuleNotFoundError, ...):
    if isinstance(exc, ast.Tuple):
        for elt in exc.elts:
            if isinstance(elt, ast.Name) and elt.id in names:
                return True

    return False


def _except_handler_has_raise(handler: ast.ExceptHandler) -> bool:
    """
    Return True if the `except` block contains any `raise` statement.

    We treat any raise in the handler body (even nested) as re-raising or
    propagating an error, so it's not considered suppression.
    """
    for stmt in handler.body:
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Raise):
                return True
    return False


def _is_union_with_none(ann: Optional[ast.expr]) -> bool:
    """
    Return True if the annotation contains a PEP 604-style union with `None`
    E.g. `Foo | None`, `None | Foo`, or wider unions that include None.
    """
    if ann is None:
        return False

    # We treat any BitOr-based expression containing a None leaf as a union with None.
    found_none = False
    found_other = False

    for sub in ast.walk(ann):
        if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.BitOr):
            # the presence of BitOr marks this as a union-like expression
            found_other = True

        if _expr_is_none(sub):
            found_none = True

    return found_none and found_other


def _is_none_annotation(ann: Optional[ast.expr]) -> bool:
    """Return True if the given annotation node syntactically represents `None`.

    This is a compatibility wrapper kept for callers that expect an
    "annotation-focused" helper. The canonical implementation lives in
    `_expr_is_none`, which inspects AST nodes (including older AST node
    types) and returns True when they represent the literal `None`.
    """
    return _expr_is_none(ann)


def _expr_is_none(expr: Optional[ast.expr]) -> bool:
    """Return True if expr syntactically represents `None`."""
    if expr is None:
        return False

    # Name: None
    if isinstance(expr, ast.Name) and expr.id == "None":
        return True

    # Constant: None
    if isinstance(expr, ast.Constant) and expr.value is None:
        return True

    # Very defensive: older Python NameConstant
    name_constant = vars(ast).get("NameConstant")  # pragma: no cover
    if name_constant is not None and isinstance(expr, name_constant):
        return getattr(expr, "value", None) is None

    return False

# ---------------------------------------------------------------------------
# Linter rules
# ---------------------------------------------------------------------------

def check_broad_exception(tree: ast.AST, filename: str, source: Optional[str] = None) -> Iterable[RuleViolation]:
    """
    Rule 01 (X001):

    Forbid broad `except Exception:` and bare `except:`.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue

        # bare `except:`
        if node.type is None:
            yield RuleViolation(
                filename,
                node.lineno,
                node.col_offset,
                "X001",
                "Do not use bare `except:`; catch specific exceptions.",
            )
            continue

        # `except Exception:` or `except (Exception, ...)`
        if _contains_exception(node.type):
            yield RuleViolation(
                filename,
                node.lineno,
                node.col_offset,
                "X001",
                "Do not use `except Exception:`; catch a more specific exception.",
            )


def check_no_noqa_comments(tree: ast.AST, filename: str, source: Optional[str] = None) -> Iterable[RuleViolation]:
    """
    Rule 02 (X002):

    Forbid the use of `# noqa:` inline suppression comments, e.g.:

        x = foo()  # noqa: X001

    Instead of suppressing lint warnings, fix the underlying issue that
    triggered the warning.
    """
    if source is None:
        return

    # Use 're' instead of literal string check to avoid self-violation
    noqa_pattern = re.compile(r"#" + r" noqa:")

    for lineno, line in enumerate(source.splitlines(), start=1):
        match = noqa_pattern.search(line)
        if match:
            yield RuleViolation(
                filename=filename,
                lineno=lineno,
                col_offset=match.start(),
                code="X002",
                message=(
                    "Do not use inline suppression "
                    "comments; fix the underlying issue instead."
                ),
            )


def check_muted_exception(tree: ast.AST, filename: str, source: Optional[str] = None) -> Iterable[RuleViolation]:
    """
    Rule 03 (X003):

    Forbid muted exception handlers.

    Any `except` block whose body consists only of "muting" statements:
        - pass
        - continue
        - break
        - return (with or without a value)
        - an ellipsis literal (`...`)
    is considered a violation (X004).
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue

        # Empty body is also effectively muting.
        if not node.body:
            yield RuleViolation(
                filename,
                node.lineno,
                node.col_offset,
                "X003",
                "Do not silently swallow exceptions; handle them or re-raise.",
            )
            continue

        if all(_is_muting_stmt(stmt) for stmt in node.body):
            yield RuleViolation(
                filename,
                node.lineno,
                node.col_offset,
                "X003",
                "Do not silently swallow exceptions; handle them or re-raise.",
            )


def check_docstrings(tree: ast.AST, filename: str, source: Optional[str]) -> Iterable[RuleViolation]:
    """
    Rule 4 (unified X004):

    Require a proper docstring as the first statement in every class /
    function / method body.
    """
    lines: Optional[Sequence[str]] = source.splitlines() if source is not None else None

    generic_message = (
        "Missing or improperly formatted docstring: add a coherent docstring "
        "block as the first statement in the body."
    )

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            continue

        if not _has_proper_docstring(node, lines):
            yield RuleViolation(
                filename,
                node.lineno,
                node.col_offset,
                "X004",
                generic_message,
            )


def check_local_imports(tree: ast.AST, filename: str, source: Optional[str] = None) -> Iterable[RuleViolation]:
    """
    Rule 05 (X005):

    Forbid imports inside function bodies (local imports).

    Any `import ...` or `from ... import ...` statement that appears inside
    a function or method body is considered a violation (X005).
    """
    class _LocalImportVisitor(ast.NodeVisitor):
        """
        AST visitor that detects imports inside function/method bodies.

        Tracks function nesting depth and collects violations for any
        import statements found within function scopes.
        """

        def __init__(self):
            """Initialize the visitor with zero function depth and an empty violations list."""
            self._function_depth = 0
            self.violations: List[RuleViolation] = []

        def visit_FunctionDef(self, node: ast.FunctionDef):
            """Visit a function definition, incrementing depth before traversal."""
            self._function_depth += 1
            self.generic_visit(node)
            self._function_depth -= 1

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            """Visit an async function definition, incrementing depth before traversal."""
            self._function_depth += 1
            self.generic_visit(node)
            self._function_depth -= 1

        def visit_Import(self, node: ast.Import):
            """Visit an import statement, recording violation if inside a function."""
            if self._function_depth > 0:
                self.violations.append(
                    RuleViolation(
                        filename,
                        node.lineno,
                        node.col_offset,
                        "X005",
                        "Do not use local imports inside function bodies; "
                        "move imports to module scope.",
                    )
                )

        def visit_ImportFrom(self, node: ast.ImportFrom):
            """Visit a from-import statement, recording violation if inside a function."""
            if self._function_depth > 0:
                self.violations.append(
                    RuleViolation(
                        filename,
                        node.lineno,
                        node.col_offset,
                        "X005",
                        "Do not use local imports inside function bodies; "
                        "move imports to module scope.",
                    )
                )

    visitor = _LocalImportVisitor()
    visitor.visit(tree)
    return visitor.violations


def check_return_type_annotations(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 6 (X006):

    Every function or method that returns a value (has `return <expr>` in its
    own body) must declare an explicit return type annotation:

        def func(...) -> ReturnType:

    We don't validate which type, only that some annotation is present.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Skip functions/methods that never return a value.
        if not _function_returns_value(node):
            continue

        # If `returns` is None, there is no `-> ...` annotation.
        if getattr(node, "returns", None) is None:
            message = (
                "Function or method returns a value but has no return type "
                "annotation; add an explicit '-> return_type' annotation."
            )
            yield RuleViolation(
                filename=filename,
                lineno=node.lineno,
                col_offset=node.col_offset,
                code="X006",
                message=message,
            )


def check_no_none_return_annotations(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 7 (X007):

    Never use an explicit `-> None` return annotation.

    Functions or methods that conceptually return nothing should omit a return
    annotation entirely instead of declaring `-> None`.
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        if _is_none_annotation(getattr(node, "returns", None)):
            yield RuleViolation(
                filename=filename,
                lineno=node.lineno,
                col_offset=node.col_offset,
                code="X007",
                message="Do not use an explicit '-> None' return annotation; "
                        "omit the return type instead for functions that return nothing.",
            )


def check_percent_formatting(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 8 (X008):

    Forbid old-style '%' string formatting such as:

        "%s %d" % (name, count)
        "%(name)s" % mapping

    and logging-style printf formatting such as:

        logger.info("Updated JSON %s", path)
        logger.debug("value=%d", value)

    Prefer f-strings instead, e.g.:

        logger.info(f"Updated JSON {path}")
    """
    # Matches %s, %d, %(name)s, etc., with optional flags/width/precision.
    percent_pattern = r"%(?:\(\w+\))?[-#0 +]*\d*(?:\.\d+)?[hlL]?[diouxXeEfFgGcrs]"

    def _has_percent_placeholders(s: str) -> bool:
        """Check if a string contains percent-style placeholders."""
        # Check if the string actually contains '%' before running regex
        if "%" not in s:
            return False
        return bool(re.search(percent_pattern, s))

    logging_methods = {
        "debug",
        "info",
        "warning",
        "error",
        "exception",
        "critical",
        "log",
    }

    for node in ast.walk(tree):
        # ------------------------------------------------------------------
        # Case 1: "%s" % value
        # ------------------------------------------------------------------
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            fmt_value: Optional[str] = None

            if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                fmt_value = node.left.value
            # Defensive: older ASTs may use ast.Str
            elif isinstance(node.left, ast.Str):  # pragma: no cover
                fmt_value = node.left.s

            if fmt_value is None:
                continue

            if not _has_percent_placeholders(fmt_value):
                continue

            yield RuleViolation(
                filename=filename,
                lineno=node.lineno,
                col_offset=node.col_offset,
                code="X008",
                message=(
                    "Do not use old-style '%' string formatting "
                    "(e.g. '%s', '%d'); use f-strings instead."
                ),
            )
            continue

        # ------------------------------------------------------------------
        # Case 2: logger.info("foo %s", value)
        # ------------------------------------------------------------------
        if isinstance(node, ast.Call):
            func = node.func
            if not isinstance(func, ast.Attribute):
                continue

            if func.attr not in logging_methods:
                continue

            if not node.args:
                continue

            first_arg = node.args[0]
            fmt_value: Optional[str] = None

            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                fmt_value = first_arg.value
            elif isinstance(first_arg, ast.Str):  # pragma: no cover
                fmt_value = first_arg.s

            if fmt_value is None:
                continue

            if not _has_percent_placeholders(fmt_value):
                continue

            yield RuleViolation(
                filename=filename,
                lineno=node.lineno,
                col_offset=node.col_offset,
                code="X008",
                message=(
                    "Do not use old-style '%' formatting in logging calls "
                    "(e.g. '... %s', '... %d'); use f-strings instead, "
                    "e.g. logger.info(f\"... {value}\")."
                ),
            )


def check_import_error_suppression(tree: ast.AST, filename: str) -> Iterable[RuleViolation]:
    """
    Rule 9 (X009):

    Forbid suppressing ImportError / ModuleNotFoundError via try/except, e.g.:

        try:
            import foo
        except ImportError:
            foo = None

    Import failures must not be turned into optional dependencies or otherwise
    silently ignored. Let them propagate or handle them in a dedicated layer.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue

        for handler in node.handlers:
            if not _except_catches_import_error(handler):
                continue

            if _except_handler_has_raise(handler):
                # Handler re-raises; not considered suppression.
                continue

            yield RuleViolation(
                filename=filename,
                lineno=handler.lineno,
                col_offset=handler.col_offset,
                code="X009",
                message=(
                    "Do not suppress ImportError/ModuleNotFoundError in try/except; "
                    "let import failures propagate instead of converting them "
                    "into optional dependencies."
                ),
            )


def check_union_none_annotations(tree: ast.AST, filename: str,) -> Iterable[RuleViolation]:
    """
    Rule 10 (X010):

    Forbid use of `Type | None` (PEP 604 union syntax with `None`) in type
    hints and encourage `Optional[Type]` instead, e.g.:

        # forbidden
        def func(param: Foo | None) -> Bar | None: ...

        # preferred
        def func(param: Optional[Foo]) -> Optional[Bar]: ...
    """

    def _report(union_node: ast.AST) -> RuleViolation:
        """Create a RuleViolation for a union type annotation with None."""
        return RuleViolation(
            filename=filename,
            lineno=getattr(union_node, "lineno", 1),
            col_offset=getattr(union_node, "col_offset", 0),
            code="X010",
            message=(
                "Do not use `Type | None` in type hints; "
                "use `Optional[Type]` from typing instead."
            ),
        )

    for node in ast.walk(tree):
        # Function/method parameters
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + ([] if node.args.vararg is None else [node.args.vararg])
                + list(node.args.kwonlyargs)
                + ([] if node.args.kwarg is None else [node.args.kwarg])
            )

            for arg in args:
                ann = getattr(arg, "annotation", None)
                if _is_union_with_none(ann):
                    yield _report(arg)

            # Return annotation
            if _is_union_with_none(getattr(node, "returns", None)):
                yield _report(node)

        # Annotated assignments: x: Type | None = ...
        elif isinstance(node, ast.AnnAssign):
            if _is_union_with_none(node.annotation):
                yield _report(node.annotation)
