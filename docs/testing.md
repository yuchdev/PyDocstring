# Testing Guide

## Running Tests

```bash
# Run all tests quietly
uv run pytest -q

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=pydocstring --cov-report=term-missing
```

## Test Structure

```
tests/
├── __init__.py
├── test_models.py           # Data model tests
├── test_detector.py         # Style detection tests
├── test_normalize.py        # Indentation/newline normalization tests
├── test_parser_google.py    # Google-style parser tests
├── test_parser_sphinx.py    # Sphinx-style parser tests
├── test_renderers.py        # Renderer output tests
├── test_rewriter.py         # CST-based source rewriter tests
├── test_converter.py        # High-level converter API tests
├── test_integration.py      # End-to-end integration tests
└── fixtures/
    └── projects/
        ├── google_to_sphinx/
        │   └── basic_project/
        │       ├── input/sample.py     # Google-style input
        │       └── expected/sample.py  # Expected Sphinx output
        ├── sphinx_to_google/
        │   └── basic_project/
        │       ├── input/sample.py     # Sphinx-style input
        │       └── expected/sample.py  # Expected Google output
        └── roundtrip/
            └── basic_project/
                └── sample.py           # Roundtrip source
```

## Unit Tests

### `test_detector.py`
Tests for `detect_style()`:
- Google-only docstrings → `DocstringStyle.GOOGLE`
- Sphinx-only docstrings → `DocstringStyle.SPHINX`
- Mixed content → detected with warnings
- Summary-only → graceful fallback

### `test_parser_google.py`
Tests for `parse_google()`:
- Summary only
- Summary + extended description
- `Args:` with types, without types
- `*args` and `**kwargs`
- `Returns:` with and without type
- `Yields:`
- `Raises:` (multiple exceptions)
- Custom sections (Examples, Notes, Warning)
- Multiline parameter descriptions
- Complex types (`Optional[str]`, `list[dict]`, `str | None`)

### `test_parser_sphinx.py`
Tests for `parse_sphinx()`:
- Summary only
- `:param name:` and `:param type name:`
- `:type name:` on separate lines
- `:returns:` and `:rtype:`
- `:raises ExcType:`
- `:yields:`

### `test_renderers.py`
Tests for `render_google()` and `render_sphinx()`:
- Round-trip: parse → render produces equivalent output
- Google → Sphinx conversion
- Sphinx → Google conversion

### `test_rewriter.py`
Tests for `rewrite_source()`:
- Module, class, function, async function docstrings
- Nested classes and functions
- Source with no docstrings (unchanged)
- CRLF line endings preserved
- Indentation preserved

## Integration Tests

### Fixture tests
`test_fixture_google_to_sphinx_matches_expected` and
`test_fixture_sphinx_to_google_matches_expected` copy fixture input
files to a temp directory, run `convert_project`, and compare the
result byte-for-byte to the expected output.

### Runtime `__doc__` tests
`test_google_to_sphinx_doc_attributes` and
`test_sphinx_to_google_doc_attributes` verify that after conversion,
**importing the rewritten module** returns the correct `__doc__`
values on functions, classes, and methods.

This is the critical proof that source rewriting affects runtime behavior.

Example assertion:
```python
# After Google → Sphinx conversion and import:
assert ":param x:" in mod.my_function.__doc__
assert "Args:" not in mod.my_function.__doc__
```

## Adding New Tests

### New unit test
Add a test function to the appropriate `test_*.py` file.

### New fixture project
1. Create `tests/fixtures/projects/<direction>/<name>/input/` with source files.
2. Run the converter on the input to generate expected output:
   ```bash
   uv run python -c "
   from pydocstring.converter import convert_project
   from pathlib import Path
   result = convert_project(Path('tests/fixtures/projects/<direction>/<name>/input'), target_style='<style>', dry_run=True)
   print(result.file_results[0].converted_source)
   "
   ```
3. Place the expected output in `tests/fixtures/projects/<direction>/<name>/expected/`.
4. Add a test in `test_integration.py` using the pattern from existing fixture tests.
