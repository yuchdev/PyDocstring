# PyDocstring

**PyDocstring** converts Python docstrings between [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) and [Sphinx (reStructuredText) style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) by rewriting Python source files in-place.

> **Important:** This tool operates on **project paths**, not free-form strings. It recursively walks a Python project directory, rewrites `.py` source files, and the resulting changes are reflected in `__doc__` attributes after import.

---

## Supported Docstring Styles

| Style   | Example |
|---------|---------|
| Google  | `Args:`, `Returns:`, `Raises:`, `Yields:` sections with indented content |
| Sphinx  | `:param name:`, `:type name:`, `:returns:`, `:rtype:`, `:raises ExcType:` field lists |

## Limitations

- Explicit `__doc__` assignments (e.g. `func.__doc__ = "..."`) are left unchanged with a warning.
- Concatenated string docstrings (`"part1" "part2"`) are left unchanged.
- Formatted strings (`f"..."`) used as docstrings are left unchanged.
- Very complex mixed styles may not round-trip perfectly; always review diffs before committing.

---

## Setup with uv

```bash
# Install uv (if not already installed)
pip install uv

# Install the tool
uv tool install pydocstring

# Or add as a project dependency
uv add pydocstring
```

---

## CLI Examples

```bash
# Convert a project from Google to Sphinx style (in-place)
pydocstring /path/to/myproject --to sphinx

# Convert from Sphinx to Google style (in-place)
pydocstring /path/to/myproject --to google

# Dry-run: show what would change without writing
pydocstring /path/to/myproject --to sphinx --dry-run

# Check mode: exit 1 if any file needs conversion
pydocstring /path/to/myproject --to sphinx --check

# Diff mode: show unified diffs
pydocstring /path/to/myproject --to sphinx --diff

# Verbose output
pydocstring /path/to/myproject --to sphinx --verbose

# Exclude files matching a glob
pydocstring /path/to/myproject --to sphinx --exclude "tests/**"

# Include only specific files
pydocstring /path/to/myproject --to sphinx --include "src/**"

# Override source style detection
pydocstring /path/to/myproject --to sphinx --from google

# Save a JSON report
pydocstring /path/to/myproject --to sphinx --json-report report.json
```

---

## Library API

```python
from pathlib import Path
from pydocstring import convert_project, convert_file, detect_docstring_style, scan_project

# Convert an entire project in-place
result = convert_project(Path("myproject"), target_style="sphinx")
print(f"Changed {result.files_changed} of {result.files_processed} files")

# Convert a single file
result = convert_file(Path("mymodule.py"), target_style="google")
print(result.converted_source)

# Detect the style of a docstring
detection = detect_docstring_style("Args:\n    x (int): value\n")
print(detection.style)  # DocstringStyle.GOOGLE

# Scan a project for Python files
files = scan_project(Path("myproject"))
for f in files:
    print(f.path)
```

---

## Check/Diff Workflow

Use `--check` in CI to ensure a project conforms to a target style:

```bash
# In CI: fail if any docstring is not Sphinx-style
pydocstring . --to sphinx --check
```

Use `--diff` to review changes before applying:

```bash
pydocstring . --to sphinx --diff | less
```

---

## Development

```bash
# Clone and set up
git clone https://github.com/yuchdev/PyDocstring
cd PyDocstring
uv sync

# Run tests
uv run pytest -q

# Run the CLI
uv run pydocstring --help
```
