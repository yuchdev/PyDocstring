# Architecture

## Overview

PyDocstring is organized as a pipeline:

```
Project path
    └── project_scanner.py   → discovers .py files
         └── rewriter.py     → per-file CST-based rewrite
              ├── detector.py     → identify source style
              ├── parser_google.py / parser_sphinx.py  → parse to model
              ├── models.py       → intermediate representation
              └── renderer_google.py / renderer_sphinx.py → render output
```

## Module Descriptions

### `models.py`
Defines the structured intermediate representation of a docstring:

- `ParsedDocstring` — the complete model with summary, extended description, params, returns, yields, raises, and custom sections.
- `ParamDoc`, `ReturnsDoc`, `YieldsDoc`, `RaisesDoc`, `SectionDoc` — sub-models.
- `DocstringStyle` — enum: `GOOGLE`, `SPHINX`, `MIXED`, `UNKNOWN`.
- `StyleDetectionResult`, `FileConversionResult`, `ProjectConversionResult`, `PythonFileInfo` — result models.

### `detector.py`
Heuristic detection of docstring style. Uses pattern matching to identify Google-style section headers (`Args:`, `Returns:`, etc.) and Sphinx-style field list markers (`:param`, `:type`, `:returns:`, etc.). Returns a confidence score and list of evidence strings.

### `parser_google.py`
Parses Google-style docstrings into `ParsedDocstring`. Handles:
- Summary and extended description
- Typed and untyped parameters
- `*args` and `**kwargs`
- Multiline parameter descriptions
- All standard sections

### `parser_sphinx.py`
Parses Sphinx field list docstrings into `ParsedDocstring`. Handles:
- Text before field list as summary/description
- `:param name:`, `:param type name:`, `:type name:`
- `:returns:`, `:return:`, `:rtype:`
- `:raises ExcType:`, `:yields:`
- Mixed content with Google-style custom sections

### `renderer_google.py`
Renders a `ParsedDocstring` to Google-style string output.

### `renderer_sphinx.py`
Renders a `ParsedDocstring` to Sphinx field list string output.

### `normalize.py`
Utilities for:
- Detecting indentation style (spaces vs tabs)
- Detecting newline style (LF vs CRLF)
- Stripping/wrapping triple-quote markers

### `rewriter.py`
Uses `libcst` to parse Python source into a Concrete Syntax Tree, visit all docstring-bearing nodes (module, class, function, async function), detect/parse/render/replace the docstring, and emit the updated source. Preserves all surrounding code unchanged.

### `project_scanner.py`
Walks a project directory tree, filtering `.py` files by include/exclude globs. Detects encoding and newline style per file.

### `converter.py`
High-level API wrapping the scanner and rewriter. Provides `convert_file`, `convert_project`, and `detect_docstring_style`.

### `cli.py`
Click-based CLI entry point (`pydocstring` command). Supports `convert` subcommand with all flags.

## Data Flow

```
Source file (.py)
    → read with detected encoding
    → rewrite_source(source, target_style)
        → libcst.parse_module(source)
        → DocstringTransformer.visit(tree)
            for each docstring node:
                → detect_style(raw_text) → DocstringStyle
                → parse_google/parse_sphinx(text) → ParsedDocstring
                → render_sphinx/render_google(parsed) → new_text
                → replace node value in CST
        → modified_tree.code
    → write back with original encoding/newline
```

## Design Decisions

- **libcst over ast**: libcst preserves comments, formatting, and whitespace. Plain `ast` cannot reconstruct source.
- **Structured intermediate model**: Avoids regex-based source transforms that would be brittle. Parsing to a model and rendering from a model is more robust.
- **Per-docstring detection**: Each docstring is individually detected rather than assuming a uniform project style, to handle mixed-style codebases.
- **Fail-safe**: If a docstring cannot be parsed or converted, it is left unchanged and a warning is emitted. Source files are never silently corrupted.
