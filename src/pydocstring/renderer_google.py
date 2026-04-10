"""Render ParsedDocstring to Google-style string."""

from __future__ import annotations

from typing import Optional

from pydocstring.models import ParsedDocstring


def render_google(doc: ParsedDocstring, indent: Optional[str] = None) -> str:
    """Render a ParsedDocstring to a Google-style docstring string."""
    parts = []
    if indent is None:
        indent = "    "

    if doc.summary:
        parts.append(doc.summary)

    if doc.extended_description:
        parts.append("")
        parts.append(doc.extended_description)

    if doc.params:
        parts.append("")
        parts.append("Args:")
        for param in doc.params:
            if param.type_annotation:
                header = f"{indent}{param.name} ({param.type_annotation}):"
            else:
                header = f"{indent}{param.name}:"
            if param.description:
                parts.append(f"{header} {param.description}")
            else:
                parts.append(header)

    if doc.returns is not None:
        parts.append("")
        parts.append("Returns:")
        ret = doc.returns
        if ret.type_annotation and ret.description:
            parts.append(f"{indent}{ret.type_annotation}: {ret.description}")
        elif ret.type_annotation:
            parts.append(f"{indent}{ret.type_annotation}")
        elif ret.description:
            parts.append(f"{indent}{ret.description}")

    if doc.yields is not None:
        parts.append("")
        parts.append("Yields:")
        yld = doc.yields
        if yld.type_annotation and yld.description:
            parts.append(f"{indent}{yld.type_annotation}: {yld.description}")
        elif yld.type_annotation:
            parts.append(f"{indent}{yld.type_annotation}")
        elif yld.description:
            parts.append(f"{indent}{yld.description}")

    if doc.raises:
        parts.append("")
        parts.append("Raises:")
        for exc in doc.raises:
            if exc.description:
                parts.append(f"{indent}{exc.exc_type}: {exc.description}")
            else:
                parts.append(f"{indent}{exc.exc_type}:")

    for section in doc.custom_sections:
        parts.append("")
        parts.append(f"{section.title}:")
        if section.content:
            for line in section.content.split("\n"):
                if line.strip():
                    parts.append(f"{indent}{line}")
                else:
                    parts.append("")

    return "\n".join(parts)
