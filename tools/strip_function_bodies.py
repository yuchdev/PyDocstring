#!/usr/bin/env python3
"""Strip Python function/method implementations while preserving docstrings.

This utility recursively walks Python files under a path and rewrites each
function or method body so that only its existing docstring (if present)
remains, followed by ``pass``.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Edit:
    start: int
    end: int
    replacement: str


def _is_docstring_stmt(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(getattr(stmt, "value", None), ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def _line_start_offsets(source: str) -> list[int]:
    offsets = [0]
    running = 0
    for line in source.splitlines(keepends=True):
        running += len(line)
        offsets.append(running)
    return offsets


def _offset(line_starts: list[int], lineno: int, col_offset: int) -> int:
    return line_starts[lineno - 1] + col_offset


def _source_segment(source: str, line_starts: list[int], node: ast.AST) -> str:
    return source[
        _offset(line_starts, node.lineno, node.col_offset) : _offset(
            line_starts, node.end_lineno, node.end_col_offset
        )
    ]


def _iter_top_level_function_nodes(tree: ast.AST) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    stack: list[tuple[ast.AST, bool]] = [(tree, False)]
    while stack:
        node, inside_function = stack.pop()
        is_function = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        if is_function and not inside_function:
            yield node
        child_inside_function = inside_function or is_function
        for child in ast.iter_child_nodes(node):
            stack.append((child, child_inside_function))


def strip_function_bodies(source: str) -> str:
    tree = ast.parse(source)
    line_starts = _line_start_offsets(source)
    edits: list[Edit] = []

    for func in _iter_top_level_function_nodes(tree):
        if not func.body:
            continue

        first_stmt = func.body[0]
        last_stmt = func.body[-1]
        body_start = _offset(line_starts, first_stmt.lineno, first_stmt.col_offset)
        body_end = _offset(line_starts, last_stmt.end_lineno, last_stmt.end_col_offset)

        indent = source[_offset(line_starts, first_stmt.lineno, 0) : body_start]

        new_body_lines: list[str] = []
        if _is_docstring_stmt(first_stmt):
            new_body_lines.append(_source_segment(source, line_starts, first_stmt))

        new_body_lines.append(f"{indent}pass")
        replacement = "\n".join(new_body_lines)

        edits.append(Edit(start=body_start, end=body_end, replacement=replacement))

    updated = source
    for edit in sorted(edits, key=lambda e: e.start, reverse=True):
        updated = updated[: edit.start] + edit.replacement + updated[edit.end :]

    return updated


def iter_python_files(path: Path) -> Iterable[Path]:
    if path.is_file() and path.suffix == ".py":
        yield path
        return

    if path.is_dir():
        for file_path in sorted(path.rglob("*.py")):
            if file_path.is_file():
                yield file_path


def rewrite_paths(paths: list[Path], dry_run: bool = False) -> int:
    changed = 0
    for target in paths:
        for py_file in iter_python_files(target):
            source = py_file.read_text(encoding="utf-8")
            rewritten = strip_function_bodies(source)
            if rewritten == source:
                continue
            changed += 1
            if dry_run:
                print(f"would update: {py_file}")
                continue
            py_file.write_text(rewritten, encoding="utf-8")
            print(f"updated: {py_file}")

    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively strip Python function/method bodies, leaving only an "
            "existing docstring (if present) and pass."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="File(s) or directory path(s) to process.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print which files would be rewritten.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed = rewrite_paths(args.paths, dry_run=args.dry_run)
    if args.dry_run:
        print(f"files that would change: {changed}")
    else:
        print(f"files changed: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
