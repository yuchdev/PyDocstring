"""Argparse-based CLI for pydocstring."""

from __future__ import annotations
import argparse
import json
import sys
import difflib
from pathlib import Path
from typing import Optional
from pydocstring.converter import convert_project


def _existing_dir(path_str: str) -> Path:
    """Argparse type: ensure path exists and is a directory, return Path."""
    p = Path(path_str)
    if not p.exists() or not p.is_dir():
        raise argparse.ArgumentTypeError(f"Path does not exist or is not a directory: {path_str}")
    return p


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pydocstring",
        description="PyDocstring - Convert Python docstrings between Google and Sphinx styles.",
    )

    parser.add_argument("project_root", type=_existing_dir, help="Project root directory")
    parser.add_argument(
        "--to",
        dest="target_style",
        choices=["google", "sphinx"],
        required=True,
        help="Target docstring style",
    )
    parser.add_argument(
        "--from",
        dest="source_style",
        choices=["google", "sphinx", "auto"],
        default="auto",
        help="Source docstring style (default: auto-detect)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write files, just show what would change",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with code 1 if any file would change",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print unified diffs without writing",
    )
    parser.add_argument(
        "--include",
        dest="include_globs",
        metavar="GLOB",
        action="append",
        default=None,
        help="Include files matching glob pattern (can be repeated)",
    )
    parser.add_argument(
        "--exclude",
        dest="exclude_globs",
        metavar="GLOB",
        action="append",
        default=None,
        help="Exclude files matching glob pattern (can be repeated)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show each file processed",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress output except errors",
    )
    parser.add_argument(
        "--json-report",
        dest="json_report",
        type=Path,
        default=None,
        help="Write JSON report to file",
    )

    return parser


def _cmd_convert(
    project_root: Path,
    target_style: str,
    source_style: str,
    dry_run: bool,
    check: bool,
    diff: bool,
    include_globs: Optional[list[str]],
    exclude_globs: Optional[list[str]],
    verbose: bool,
    quiet: bool,
    json_report: Optional[Path],
) -> int:
    """Run convert command; return exit code."""
    effective_dry_run = dry_run or check or diff

    result = convert_project(
        root=project_root,
        target_style=target_style,
        source_style=source_style if source_style != "auto" else None,
        include_globs=list(include_globs) if include_globs else None,
        exclude_globs=list(exclude_globs) if exclude_globs else None,
        dry_run=effective_dry_run,
    )

    if not quiet:
        for file_result in result.file_results:
            rel = (
                file_result.path.relative_to(project_root)
                if file_result.path.is_relative_to(project_root)
                else file_result.path
            )

            if file_result.error:
                print(f"ERROR {rel}: {file_result.error}", file=sys.stderr)
            elif file_result.changed:
                if verbose or diff or dry_run:
                    print(f"{'Would change' if effective_dry_run else 'Changed'}: {rel}")
                if diff:
                    original_lines = file_result.original_source.splitlines(keepends=True)
                    converted_lines = file_result.converted_source.splitlines(keepends=True)
                    diff_lines = difflib.unified_diff(
                        original_lines,
                        converted_lines,
                        fromfile=str(rel),
                        tofile=str(rel) + " (converted)",
                    )
                    # unified_diff returns an iterator of lines already containing newlines
                    sys.stdout.write("".join(diff_lines))
            elif verbose:
                print(f"Unchanged: {rel}")

        if result.warnings and not quiet:
            for w in result.warnings:
                print(f"Warning: {w}", file=sys.stderr)

        if not quiet:
            print(
                f"\nProcessed {result.files_processed} files, "
                f"{result.files_changed} changed, "
                f"{result.files_skipped} skipped."
            )

    if json_report:
        report_data = {
            "root": str(result.root),
            "files_processed": result.files_processed,
            "files_changed": result.files_changed,
            "files_skipped": result.files_skipped,
            "warnings": result.warnings,
            "files": [
                {
                    "path": str(fr.path),
                    "changed": fr.changed,
                    "error": fr.error,
                    "warnings": fr.warnings,
                }
                for fr in result.file_results
            ],
        }
        with open(json_report, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

    if check and result.files_changed > 0:
        return 1
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Console script entry point for pydocstring."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    return _cmd_convert(
        project_root=args.project_root,
        target_style=args.target_style,
        source_style=args.source_style,
        dry_run=args.dry_run,
        check=args.check,
        diff=args.diff,
        include_globs=args.include_globs,
        exclude_globs=args.exclude_globs,
        verbose=args.verbose,
        quiet=args.quiet,
        json_report=args.json_report,
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
