"""Custom AST-based linter for PyDocstring coding standards."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    """A single lint violation."""

    path: str
    line: int
    col: int
    code: str
    message: str

    def __str__(self) -> str:
        """Format the violation as a human-readable string."""
        return f"{self.path}:{self.line}:{self.col}: {self.code} {self.message}"


def check_file(path: Path) -> list[Violation]:
    """Run all lint checks on *path* and return any violations found."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    checker = _LintChecker(path=str(path))
    checker.visit(tree)
    return checker.violations


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _has_docstring(body: list[ast.stmt]) -> bool:
    """Return True when *body* starts with a string-literal docstring."""
    return (
        bool(body)
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def _returns_none_annotation(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True when *node* has an explicit ``-> None`` return annotation."""
    return (
        node.returns is not None
        and isinstance(node.returns, ast.Constant)
        and node.returns.value is None
    )


def _has_return_with_value(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True when *node* body contains at least one ``return <value>``."""
    for child in ast.walk(node):
        # Do not descend into nested function/class definitions
        if child is not node and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if isinstance(child, ast.Return) and child.value is not None:
            return True
    return False


class _LintChecker(ast.NodeVisitor):
    """Visitor that accumulates violations for a single source file."""

    def __init__(self, path: str) -> None:
        """Initialise the checker for *path*."""
        self.path = path
        self.violations: list[Violation] = []
        # Track whether we are currently inside a function body so that
        # X005 (local imports) can be detected.
        self._function_depth = 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add(self, line: int, col: int, code: str, message: str) -> None:
        """Append a violation to the internal list."""
        self.violations.append(Violation(self.path, line, col, code, message))

    # ------------------------------------------------------------------
    # Module / class / function – X004
    # ------------------------------------------------------------------

    def visit_Module(self, node: ast.Module) -> None:
        """Check module-level docstring (X004)."""
        if not _has_docstring(node.body):
            self._add(0, 0, "X004",
                      "Missing or improperly formatted docstring: add a coherent "
                      "docstring block as the first statement in the body.")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class docstring (X004)."""
        if not _has_docstring(node.body):
            self._add(node.lineno, node.col_offset, "X004",
                      "Missing or improperly formatted docstring: add a coherent "
                      "docstring block as the first statement in the body.")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function/method rules (X004, X006, X007)."""
        self._check_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function/method rules (X004, X006, X007)."""
        self._check_function(node)

    def _check_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Apply X004, X006 and X007 checks to a function or method node."""
        # X004 – missing docstring
        if not _has_docstring(node.body):
            self._add(node.lineno, node.col_offset, "X004",
                      "Missing or improperly formatted docstring: add a coherent "
                      "docstring block as the first statement in the body.")

        # X006 – returns a value but no return-type annotation
        if node.returns is None and _has_return_with_value(node):
            self._add(node.lineno, node.col_offset, "X006",
                      "Function or method returns a value but has no return type "
                      "annotation; add an explicit '-> return_type' annotation.")

        # X007 – explicit '-> None' return annotation
        if _returns_none_annotation(node):
            self._add(node.lineno, node.col_offset, "X007",
                      "Do not use an explicit '-> None' return annotation; omit the "
                      "return type instead for functions that return nothing.")

        # Descend, tracking function depth for X005
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1

    # ------------------------------------------------------------------
    # Imports inside functions – X005
    # ------------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        """Check for imports inside function bodies (X005)."""
        if self._function_depth > 0:
            self._add(node.lineno, node.col_offset, "X005",
                      "Do not use local imports inside function bodies; "
                      "move imports to module scope.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for from-imports inside function bodies (X005)."""
        if self._function_depth > 0:
            self._add(node.lineno, node.col_offset, "X005",
                      "Do not use local imports inside function bodies; "
                      "move imports to module scope.")
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Exception handlers – X001, X003
    # ------------------------------------------------------------------

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Check exception handler rules (X001, X003)."""
        # X001 – catching the bare 'Exception' class
        if (
            node.type is not None
            and isinstance(node.type, ast.Name)
            and node.type.id == "Exception"
        ):
            self._add(node.lineno, node.col_offset, "X001",
                      "Do not use `except Exception:`; catch a more specific exception.")

        # X003 – silently swallowing an exception (body is only 'pass')
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self._add(node.lineno, node.col_offset, "X003",
                      "Do not silently swallow exceptions; handle them or re-raise.")

        self.generic_visit(node)
