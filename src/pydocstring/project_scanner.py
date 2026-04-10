"""Recursive project file scanning."""
from __future__ import annotations
import fnmatch
from pathlib import Path
from pydocstring.models import PythonFileInfo


def detect_file_encoding(path: Path) -> str:
    """Detect the encoding of a file."""
    try:
        with open(path, 'rb') as f:
            raw = f.read(4)
        if raw.startswith(b'\xff\xfe'):
            return 'utf-16-le'
        elif raw.startswith(b'\xfe\xff'):
            return 'utf-16-be'
        elif raw.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
    except OSError:
        return 'utf-8'
    return 'utf-8'


def detect_file_newline(path: Path) -> str:
    """Detect the newline style of a file."""
    try:
        with open(path, 'rb') as f:
            content = f.read()
        if b'\r\n' in content:
            return '\r\n'
    except OSError:
        return '\n'
    return '\n'


def _matches_any_glob(path: Path, globs: list[str]) -> bool:
    """Check if path matches any of the given glob patterns."""
    for pattern in globs:
        if fnmatch.fnmatch(str(path), pattern):
            return True
        if fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def scan_project(
    root: Path,
    include_globs: list[str] = None,
    exclude_globs: list[str] = None,
) -> list[PythonFileInfo]:
    """Scan a project directory for Python files."""
    if include_globs is None:
        include_globs = ['*.py']
    if exclude_globs is None:
        exclude_globs = []

    results = []

    for py_file in sorted(root.rglob('*.py')):
        relative = py_file.relative_to(root)

        if exclude_globs and _matches_any_glob(relative, exclude_globs):
            continue

        if include_globs != ['*.py']:
            if not _matches_any_glob(relative, include_globs):
                continue

        encoding = detect_file_encoding(py_file)
        newline = detect_file_newline(py_file)

        results.append(PythonFileInfo(
            path=py_file,
            relative_path=relative,
            encoding=encoding,
            newline=newline,
        ))

    return results
