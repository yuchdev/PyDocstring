"""Core logic for stripping function/method implementations while preserving docstrings."""

from __future__ import annotations

import ast
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class Edit:
    """Represents a source code edit."""
    start: int
    end: int
    replacement: str


@dataclass(frozen=True)
class StripResult:
    """Result of stripping multiple files."""
    files_processed: int
    files_changed: int
    files_renamed: int
    file_results: list[FileStripResult]

@dataclass(frozen=True)
class FileStripResult:
    """Details about a single file strip operation."""
    path: Path
    original_path: Path
    changed: bool
    renamed: bool
    new_path: Optional[Path] = None


def _is_docstring_stmt(stmt: ast.stmt) -> bool:
    """Check if an AST statement is a docstring."""
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(getattr(stmt, "value", None), ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def _line_start_offsets(source: str) -> list[int]:
    """Precompute character offsets for the start of each line."""
    offsets = [0]
    running = 0
    for line in source.splitlines(keepends=True):
        running += len(line)
        offsets.append(running)
    return offsets


def _offset(line_starts: list[int], lineno: int, col_offset: int) -> int:
    """Convert line/column to absolute character offset."""
    return line_starts[lineno - 1] + col_offset


def _source_segment(source: str, line_starts: list[int], node: ast.AST) -> str:
    """Extract a source segment for an AST node."""
    return source[
        _offset(line_starts, node.lineno, node.col_offset) : _offset(
            line_starts, node.end_lineno, node.end_col_offset
        )
    ]


def _iter_top_level_function_nodes(tree: ast.AST) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Iterate over non-nested function and method definitions."""
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
    """Strip function/method implementations while preserving docstrings.

    Returns:
        The updated source code string.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

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


def _compile_rename_pattern(pattern: str) -> tuple[re.Pattern[str], int]:
    """Compile a rename pattern and extract its numeric token width."""
    token_regex = re.compile(r"\{(N+)\}")
    matches = list(token_regex.finditer(pattern))
    if len(matches) != 1:
        raise ValueError("Rename pattern must contain exactly one numeric token like {NNN}.")

    token_match = matches[0]
    width = len(token_match.group(1))
    return token_regex, width


def _render_name(pattern: str, token_regex: re.Pattern[str], width: int, index: int) -> str:
    """Render a target file name using the rename pattern."""
    formatted = str(index).zfill(width)
    return token_regex.sub(formatted, pattern, count=1)


def _build_rename_plan(files: list[Path], rename_pattern: str, start_index: int) -> list[tuple[Path, Path]]:
    """Build a list of (original_path, target_path) tuples."""
    token_regex, width = _compile_rename_pattern(rename_pattern)
    plan: list[tuple[Path, Path]] = []

    for idx, original in enumerate(files, start=start_index):
        target_name = _render_name(rename_pattern, token_regex, width, idx)
        target_path = original.with_name(target_name)
        if original != target_path:
            plan.append((original, target_path))

    destinations = [target for _, target in plan]
    if len(destinations) != len(set(destinations)):
        raise ValueError("Rename pattern generated duplicate destination file names.")

    return plan


def _apply_rename_plan(plan: list[tuple[Path, Path]], dry_run: bool) -> list[tuple[Path, Path]]:
    """Physically rename files according to the plan. Returns list of actually renamed pairs."""
    if not plan:
        return []

    if dry_run:
        return plan

    temp_mappings: list[tuple[Path, Path]] = []
    for old_path, _ in plan:
        temp_path = old_path.with_name(f".{old_path.name}.tmp-strip-{uuid.uuid4().hex}")
        old_path.rename(temp_path)
        temp_mappings.append((temp_path, old_path))

    original_to_temp = {original: temp for temp, original in temp_mappings}

    for old_path, new_path in plan:
        original_to_temp[old_path].rename(new_path)

    return plan


def strip_paths(
    paths: list[Path],
    dry_run: bool = False,
    rename_pattern: Optional[str] = None,
    start_index: int = 1,
) -> StripResult:
    """Iterate over paths and strip Python files."""
    files_processed = 0
    files_changed = 0
    python_files: list[Path] = []

    for path in paths:
        if path.is_file() and path.suffix == ".py":
            python_files.append(path)
        elif path.is_dir():
            python_files.extend(sorted(p for p in path.rglob("*.py") if p.is_file()))

    file_results: list[FileStripResult] = []
    processed_list: list[Path] = []
    for py_file in python_files:
        files_processed += 1
        processed_list.append(py_file)
        try:
            source = py_file.read_text(encoding="utf-8")
        except OSError:
            continue

        rewritten = strip_function_bodies(source)
        changed = rewritten != source
        if changed:
            files_changed += 1
            if not dry_run:
                py_file.write_text(rewritten, encoding="utf-8")

        file_results.append(
            FileStripResult(
                path=py_file,
                original_path=py_file,
                changed=changed,
                renamed=False,
            )
        )

    files_renamed = 0
    if rename_pattern is not None:
        rename_plan = _build_rename_plan(processed_list, rename_pattern, start_index=start_index)
        renamed_pairs = _apply_rename_plan(rename_plan, dry_run=dry_run)
        files_renamed = len(renamed_pairs)

        # Update file_results with rename info
        renames_dict = {old: new for old, new in renamed_pairs}
        new_file_results = []
        for res in file_results:
            if res.path in renames_dict:
                new_path = renames_dict[res.path]
                new_file_results.append(
                    FileStripResult(
                        path=new_path,
                        original_path=res.original_path,
                        changed=res.changed,
                        renamed=True,
                        new_path=new_path,
                    )
                )
            else:
                new_file_results.append(res)
        file_results = new_file_results

    return StripResult(
        files_processed=files_processed,
        files_changed=files_changed,
        files_renamed=files_renamed,
        file_results=file_results,
    )
