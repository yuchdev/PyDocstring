"""High-level conversion API."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from pydocstring.models import (
    DocstringStyle, FileConversionResult, ProjectConversionResult,
    StyleDetectionResult,
)
from pydocstring.detector import detect_style
from pydocstring.rewriter import rewrite_source
from pydocstring.project_scanner import scan_project


def _parse_style(style_str: Optional[str]) -> Optional[DocstringStyle]:
    if style_str is None or style_str == 'auto':
        return None
    return DocstringStyle(style_str.lower())


def detect_docstring_style(text: str) -> StyleDetectionResult:
    """Detect the docstring style of the given text."""
    return detect_style(text)


def convert_file(
    path: Path,
    target_style: str,
    source_style: str = None,
    dry_run: bool = False,
) -> FileConversionResult:
    """Convert docstrings in a single file."""
    result = FileConversionResult(path=path)

    try:
        encoding = 'utf-8'
        try:
            from pydocstring.project_scanner import detect_file_encoding, detect_file_newline
            encoding = detect_file_encoding(path)
            newline = detect_file_newline(path)
        except Exception:
            newline = '\n'

        with open(path, encoding=encoding, errors='replace', newline='') as f:
            source = f.read()

        result.original_source = source

        target = DocstringStyle(target_style.lower())
        source_style_enum = _parse_style(source_style)

        warnings = []
        converted = rewrite_source(
            source,
            target_style=target,
            source_style=source_style_enum,
            warnings=warnings,
        )
        result.warnings = warnings
        result.converted_source = converted
        result.changed = converted != source

        if result.changed and not dry_run:
            with open(path, 'w', encoding=encoding, newline='') as f:
                f.write(converted)

    except Exception as e:
        result.error = str(e)

    return result


def convert_project(
    root: Path,
    target_style: str,
    source_style: str = None,
    include_globs: list[str] = None,
    exclude_globs: list[str] = None,
    dry_run: bool = False,
) -> ProjectConversionResult:
    """Convert docstrings in an entire project."""
    result = ProjectConversionResult(root=root)

    files = scan_project(root, include_globs=include_globs, exclude_globs=exclude_globs)

    for file_info in files:
        result.files_processed += 1
        file_result = convert_file(
            file_info.path,
            target_style=target_style,
            source_style=source_style,
            dry_run=dry_run,
        )
        result.file_results.append(file_result)

        if file_result.error:
            result.files_skipped += 1
            result.warnings.append(f"{file_info.relative_path}: {file_result.error}")
        elif file_result.changed:
            result.files_changed += 1

        result.warnings.extend(
            f"{file_info.relative_path}: {w}" for w in file_result.warnings
        )

    return result
