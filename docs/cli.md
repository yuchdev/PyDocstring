# CLI Reference

## Installation

```bash
pip install uv
uv tool install pydocstring
```

## Commands

### `pydocstring convert`

Convert docstrings in a Python project.

```
pydocstring convert PROJECT_ROOT --to {google,sphinx} [OPTIONS]
```

**Required arguments:**

| Argument | Description |
|---|---|
| `PROJECT_ROOT` | Path to the Python project root directory |
| `--to {google,sphinx}` | Target docstring style |

**Options:**

| Option | Description |
|---|---|
| `--from {google,sphinx,auto}` | Source style (default: auto-detect per docstring) |
| `--dry-run` | Show what would change without writing files |
| `--check` | Exit with code 1 if any file would change |
| `--diff` | Print unified diffs without writing |
| `--include GLOB` | Only process files matching glob (repeatable) |
| `--exclude GLOB` | Skip files matching glob (repeatable) |
| `--verbose, -v` | Show each file being processed |
| `--quiet, -q` | Suppress all output except errors |
| `--json-report PATH` | Write JSON summary to file |

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success (or `--check` with no changes needed) |
| `1` | `--check` found files that would change, or a fatal error occurred |

## Examples

### In-place conversion

```bash
# Convert Google → Sphinx
pydocstring convert ./myproject --to sphinx

# Convert Sphinx → Google
pydocstring convert ./myproject --to google
```

### Safe workflows (inspect before writing)

```bash
# View diffs only
pydocstring convert ./myproject --to sphinx --diff

# Dry-run with verbose output
pydocstring convert ./myproject --to sphinx --dry-run --verbose
```

### CI enforcement

```bash
# Fail if project is not using Sphinx style
pydocstring convert . --to sphinx --check
```

### Selective processing

```bash
# Only convert files in src/
pydocstring convert . --to sphinx --include "src/**/*.py"

# Skip test files
pydocstring convert . --to sphinx --exclude "tests/**"

# Skip vendored code
pydocstring convert . --to sphinx --exclude "vendor/**" --exclude "third_party/**"
```

### JSON report

```bash
pydocstring convert . --to sphinx --json-report conversion_report.json
```

The JSON report has the structure:
```json
{
  "root": "/path/to/project",
  "target_style": "sphinx",
  "files_processed": 42,
  "files_changed": 15,
  "files_skipped": 0,
  "files": [
    {
      "path": "src/mymodule.py",
      "changed": true,
      "warnings": []
    }
  ],
  "warnings": []
}
```
