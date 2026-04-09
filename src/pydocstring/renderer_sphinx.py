"""Render ParsedDocstring to Sphinx-style string."""
from __future__ import annotations
from pydocstring.models import ParsedDocstring


def render_sphinx(doc: ParsedDocstring, indent: str = "    ") -> str:
    """Render a ParsedDocstring to a Sphinx-style docstring string."""
    parts = []

    if doc.summary:
        parts.append(doc.summary)

    if doc.extended_description:
        parts.append('')
        parts.append(doc.extended_description)

    has_fields = bool(doc.params or doc.returns or doc.yields or doc.raises)
    if has_fields and (doc.summary or doc.extended_description):
        parts.append('')

    for param in doc.params:
        if param.description:
            parts.append(f':param {param.name}: {param.description}')
        else:
            parts.append(f':param {param.name}:')
        if param.type_annotation:
            parts.append(f':type {param.name}: {param.type_annotation}')

    if doc.returns is not None:
        ret = doc.returns
        if ret.description:
            parts.append(f':returns: {ret.description}')
        else:
            parts.append(':returns:')
        if ret.type_annotation:
            parts.append(f':rtype: {ret.type_annotation}')

    if doc.yields is not None:
        yld = doc.yields
        if yld.description:
            parts.append(f':yields: {yld.description}')
        else:
            parts.append(':yields:')
        if yld.type_annotation:
            parts.append(f':rtype: {yld.type_annotation}')

    for exc in doc.raises:
        if exc.description:
            parts.append(f':raises {exc.exc_type}: {exc.description}')
        else:
            parts.append(f':raises {exc.exc_type}:')

    for section in doc.custom_sections:
        parts.append('')
        parts.append(f'{section.title}:')
        if section.content:
            for line in section.content.split('\n'):
                if line.strip():
                    parts.append(f'{indent}{line}')
                else:
                    parts.append('')

    return '\n'.join(parts)
