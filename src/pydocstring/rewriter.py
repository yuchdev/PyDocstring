"""CST-based source rewriter using libcst."""

from __future__ import annotations
from typing import Any, Optional
import libcst as cst
from pydocstring.models import DocstringStyle
from pydocstring.detector import detect_style
from pydocstring.parser_google import parse_google
from pydocstring.parser_sphinx import parse_sphinx
from pydocstring.renderer_google import render_google
from pydocstring.renderer_sphinx import render_sphinx


def _get_body_indent(raw_value: str, quote: str) -> str:
    """Get the indentation used in docstring body (continuation lines)."""
    after_open = raw_value[len(quote) :]
    lines = after_open.split("\n")
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped and not stripped.startswith(quote):
            return line[: len(line) - len(stripped)]
    return "    "


def _normalize_docstring_content(content: str, body_indent: str) -> str:
    """Strip body_indent from continuation lines (all lines after line 0)."""
    if not body_indent:
        return content
    lines = content.split("\n")
    if len(lines) <= 1:
        return content

    result = [lines[0]]
    for line in lines[1:]:
        if line.startswith(body_indent):
            result.append(line[len(body_indent) :])
        elif line.strip() == "":
            result.append("")
        else:
            result.append(line.lstrip() if line.lstrip() else "")
    return "\n".join(result)


def _rebuild_docstring(rendered: str, body_indent: str, quote: str) -> str:
    """Rebuild a docstring string literal from rendered content."""
    rendered = rendered.rstrip("\n")
    lines = rendered.split("\n")

    if len(lines) == 1 and "\n" not in rendered:
        return f"{quote}{rendered}{quote}"

    parts = [quote + lines[0]]
    for line in lines[1:]:
        if line.strip():
            parts.append(body_indent + line)
        else:
            parts.append("")
    parts.append(body_indent + quote)
    return "\n".join(parts)


def _parse_docstring(text: str, style: DocstringStyle) -> object:
    """Parse docstring text using the given style parser."""
    if style == DocstringStyle.SPHINX:
        return parse_sphinx(text)
    elif style in (DocstringStyle.GOOGLE, DocstringStyle.UNKNOWN):
        return parse_google(text)
    elif style == DocstringStyle.MIXED:
        return parse_sphinx(text)
    return parse_google(text)


def _render_docstring(parsed, style: DocstringStyle, indent: str = "    ") -> str:
    """Render parsed docstring using the given style renderer."""
    if style == DocstringStyle.SPHINX:
        return render_sphinx(parsed, indent=indent)
    else:
        return render_google(parsed, indent=indent)


class DocstringRewriter(cst.CSTTransformer):
    """A libcst transformer that rewrites docstrings."""

    def __init__(self, target_style: DocstringStyle, source_style: Optional[DocstringStyle] = None,
                 warnings: Optional[list] = None):
        """Initialise the rewriter with the target style and optional settings."""
        super().__init__()
        self.target_style = target_style
        self.source_style = source_style
        self.warnings = warnings if warnings is not None else []

    def _process_body(self, body: Any, node: Any) -> Any:
        """Process the body of a module/class/function to rewrite its docstring."""
        if not body:
            return node

        first = body[0]
        if not isinstance(first, cst.SimpleStatementLine):
            return node
        if len(first.body) != 1 or not isinstance(first.body[0], cst.Expr):
            return node

        expr = first.body[0]
        str_node = expr.value
        if not isinstance(str_node, cst.SimpleString):
            return node

        raw = str_node.value

        quote = None
        for q in ('"""', "'''"):
            if raw.startswith(q) or raw.startswith(f"r{q}") or raw.startswith(f"u{q}"):
                quote = q
                break
        if quote is None:
            return node

        prefix_end = raw.index(quote)
        open_quote = raw[: prefix_end + len(quote)]
        if not raw.endswith(quote):
            return node
        content = raw[len(open_quote) : -len(quote)]

        body_indent = _get_body_indent(raw, quote)

        normalized = _normalize_docstring_content(content, body_indent)

        try:
            detection = detect_style(normalized)
            effective_source = self.source_style or detection.style

            if effective_source == DocstringStyle.UNKNOWN:
                if self.target_style == DocstringStyle.SPHINX:
                    effective_source = DocstringStyle.GOOGLE
                else:
                    effective_source = DocstringStyle.SPHINX

            if effective_source == self.target_style:
                return node

            parsed = _parse_docstring(normalized, effective_source)
            rendered = _render_docstring(parsed, self.target_style, indent="    ")

            new_raw = _rebuild_docstring(rendered, body_indent, quote)
            new_str_node = str_node.with_changes(value=new_raw)
            new_expr = expr.with_changes(value=new_str_node)
            new_first = first.with_changes(body=(new_expr,))

            new_body = (new_first,) + tuple(body[1:])

            if isinstance(node, cst.Module):
                return node.with_changes(body=new_body)
            else:
                new_indented = node.body.with_changes(body=new_body)
                return node.with_changes(body=new_indented)
        except (ValueError, TypeError, RuntimeError) as e:
            self.warnings.append(f"Failed to rewrite docstring: {e}")
            return node

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        """Rewrite the module-level docstring when visiting a Module node."""
        body = updated_node.body
        return self._process_body(body, updated_node)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Rewrite function docstrings when visiting a FunctionDef node."""
        if isinstance(updated_node.body, cst.IndentedBlock):
            body = updated_node.body.body
            return self._process_body(body, updated_node)
        return updated_node

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Rewrite class docstrings when visiting a ClassDef node."""
        if isinstance(updated_node.body, cst.IndentedBlock):
            body = updated_node.body.body
            return self._process_body(body, updated_node)
        return updated_node


def rewrite_source(
    source: str,
    target_style: DocstringStyle,
    source_style: Optional[DocstringStyle] = None,
    warnings: Optional[list] = None,
) -> str:
    """Rewrite all docstrings in source code to the target style."""
    if warnings is None:
        warnings = []

    tree = cst.parse_module(source)
    rewriter = DocstringRewriter(
        target_style=target_style,
        source_style=source_style,
        warnings=warnings,
    )
    new_tree = tree.visit(rewriter)
    return new_tree.code
