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

| Argument               | Description                               |
|------------------------|-------------------------------------------|
| `PROJECT_ROOT`         | Path to the Python project root directory |
| `--to {google,sphinx}` | Target docstring style                    |

**Options:**

| Option                        | Description                                       |
|-------------------------------|---------------------------------------------------|
| `--from {google,sphinx,auto}` | Source style (default: auto-detect per docstring) |
| `--dry-run`                   | Show what would change without writing files      |
| `--check`                     | Exit with code 1 if any file would change         |
| `--diff`                      | Print unified diffs without writing               |
| `--include GLOB`              | Only process files matching glob (repeatable)     |
| `--exclude GLOB`              | Skip files matching glob (repeatable)             |
| `--verbose, -v`               | Show each file being processed                    |
| `--quiet, -q`                 | Suppress all output except errors                 |
| `--json-report PATH`          | Write JSON summary to file                        |

### `pydocstring strip`

Strip function/method bodies, leaving only docstrings and `pass`.

```
pydocstring strip PATHS [OPTIONS]
```

**Required arguments:**

| Argument | Description                                    |
|----------|------------------------------------------------|
| `PATHS`  | One or more file or directory paths to process |

**Options:**

| Option                     | Description                                            |
|----------------------------|--------------------------------------------------------|
| `--dry-run`                | Show what would change without writing files           |
| `--rename-pattern PATTERN` | Optional output name pattern, e.g. 'test_doc_{NNN}.py' |
| `--start-index INDEX`      | Starting index for numbering (default: 1)              |

## Exit Codes

| Code | Meaning                                                            |
|------|--------------------------------------------------------------------|
| `0`  | Success (or `--check` with no changes needed)                      |
| `1`  | `--check` found files that would change, or a fatal error occurred |

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

# Skip test files and vendored code
pydocstring convert . --to sphinx --exclude "tests/**" --exclude "vendor/**"

# Mix include/exclude: Only files in src/ but exclude internals
pydocstring convert . --to sphinx --include "src/**/*.py" --exclude "src/**/_internal.py"
```

### JSON report

```bash
pydocstring convert . --to sphinx --json-report conversion_report.json
```

### Body Stripping

```bash
# Strip bodies in-place
pydocstring strip ./myproject

# Strip bodies and rename files with a pattern
# This will rename processed files to test_doc_001.py, test_doc_002.py, etc.
pydocstring strip ./myproject --rename-pattern "test_doc_{NNN}.py"

# Strip bodies with a custom start index for numbering
# This will rename files to doc_10.py, doc_11.py, etc.
pydocstring strip ./myproject --rename-pattern "doc_{NN}.py" --start-index 10
```

#### Renaming Patterns

The `--rename-pattern` option uses a special token `{N...N}` to insert a zero-padded index into the resulting filenames.

- `{N}`: No padding (1, 2, 3...)
- `{NN}`: Padded to 2 digits (01, 02, 03...)
- `{NNN}`: Padded to 3 digits (001, 002, 003...)
- And so on.

> **Warning:** The renaming occurs for *every* file processed, and the tool will stop if it generates duplicate names. If you use it on a directory, it will flatten the results (all renamed files will be in their original parent directories, but with the new names).

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
