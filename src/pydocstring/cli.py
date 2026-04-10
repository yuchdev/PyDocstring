"""Click-based CLI for pydocstring."""

from __future__ import annotations
import json
import sys
import difflib
from pathlib import Path
from typing import Optional
import click
from pydocstring.converter import convert_project


@click.group()
def main():
    """PyDocstring - Convert Python docstrings between Google and Sphinx styles."""
    pass


@main.command()
@click.argument(
    "project_root", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--to",
    "target_style",
    type=click.Choice(["google", "sphinx"]),
    required=True,
    help="Target docstring style",
)
@click.option(
    "--from",
    "source_style",
    type=click.Choice(["google", "sphinx", "auto"]),
    default="auto",
    help="Source docstring style (default: auto-detect)",
)
@click.option(
    "--dry-run", is_flag=True, help="Don't write files, just show what would change"
)
@click.option("--check", is_flag=True, help="Exit with code 1 if any file would change")
@click.option("--diff", is_flag=True, help="Print unified diffs without writing")
@click.option(
    "--include",
    "include_globs",
    multiple=True,
    metavar="GLOB",
    help="Include files matching glob pattern",
)
@click.option(
    "--exclude",
    "exclude_globs",
    multiple=True,
    metavar="GLOB",
    help="Exclude files matching glob pattern",
)
@click.option("--verbose", "-v", is_flag=True, help="Show each file processed")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output except errors")
@click.option(
    "--json-report",
    type=click.Path(path_type=Path),
    default=None,
    help="Write JSON report to file",
)
def convert(
    project_root: Path,
    target_style: str,
    source_style: str,
    dry_run: bool,
    check: bool,
    diff: bool,
    include_globs: tuple,
    exclude_globs: tuple,
    verbose: bool,
    quiet: bool,
    json_report: Optional[Path],
):
    """Convert docstrings in a project."""
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
                click.echo(f"ERROR {rel}: {file_result.error}", err=True)
            elif file_result.changed:
                if verbose or diff or dry_run:
                    click.echo(
                        f"{'Would change' if effective_dry_run else 'Changed'}: {rel}"
                    )
                if diff:
                    original_lines = file_result.original_source.splitlines(
                        keepends=True
                    )
                    converted_lines = file_result.converted_source.splitlines(
                        keepends=True
                    )
                    diff_lines = difflib.unified_diff(
                        original_lines,
                        converted_lines,
                        fromfile=str(rel),
                        tofile=str(rel) + " (converted)",
                    )
                    click.echo("".join(diff_lines), nl=False)
            elif verbose:
                click.echo(f"Unchanged: {rel}")

        if result.warnings and not quiet:
            for w in result.warnings:
                click.echo(f"Warning: {w}", err=True)

        if not quiet:
            click.echo(
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
        with open(json_report, "w") as f:
            json.dump(report_data, f, indent=2)

    if check and result.files_changed > 0:
        sys.exit(1)
