"""Parse Google-style docstrings into ParsedDocstring."""
from __future__ import annotations
import re
from typing import Optional
from pydocstring.models import (
    ParsedDocstring, ParamDoc, RaisesDoc, ReturnsDoc, YieldsDoc,
    SectionDoc, DocstringStyle,
)

GOOGLE_SECTION_HEADERS = {
    'Args', 'Arguments', 'Parameters', 'Returns', 'Return', 'Yields', 'Yield',
    'Raises', 'Raise', 'Note', 'Notes', 'Example', 'Examples', 'Warning',
    'Warnings', 'Todo', 'See Also', 'References', 'Attributes',
}

SECTION_RE = re.compile(r'^(\s*)([A-Z][a-zA-Z ]*?):\s*$')

PARAM_RE = re.compile(
    r'^(\s*)(\*{0,2}\w+)\s*(?:\(([^)]*)\))?\s*:\s*(.*)'
)


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _parse_section_body(lines: list[str], section_indent: int) -> list[tuple[str, Optional[str], str]]:
    """Parse section body lines into (name, type, description) tuples."""
    items = []
    current_name = None
    current_type = None
    current_desc_lines = []

    item_indent = None

    for line in lines:
        if not line.strip():
            if current_name is not None:
                current_desc_lines.append('')
            continue

        line_indent = _get_indent(line)

        m = PARAM_RE.match(line)
        if m:
            item_line_indent = len(m.group(1))
            if item_indent is None:
                item_indent = item_line_indent

            if item_line_indent == item_indent:
                if current_name is not None:
                    desc = ' '.join(
                        l.strip() if l.strip() else '' for l in current_desc_lines
                    ).strip()
                    items.append((current_name, current_type, desc))

                current_name = m.group(2)
                current_type = m.group(3)
                if current_type:
                    current_type = current_type.strip()
                current_desc_lines = [m.group(4).strip()] if m.group(4).strip() else []
                continue

        if current_name is not None:
            current_desc_lines.append(line.strip())

    if current_name is not None:
        desc = ' '.join(
            l if l.strip() else '' for l in current_desc_lines
        ).strip()
        items.append((current_name, current_type, desc))

    return items


def _parse_returns_body(lines: list[str]) -> tuple[Optional[str], str]:
    """Parse Returns/Yields section body. Returns (type, description)."""
    if not lines:
        return None, ""

    first_content = None
    rest_lines = []
    for i, line in enumerate(lines):
        if line.strip():
            first_content = line
            rest_lines = lines[i+1:]
            break

    if first_content is None:
        return None, ""

    stripped = first_content.strip()
    colon_idx = stripped.find(':')
    if colon_idx > 0:
        potential_type = stripped[:colon_idx].strip()
        if re.match(r'^[A-Za-z][\w\[\], |.]*$', potential_type):
            desc = stripped[colon_idx+1:].strip()
            continuation = ' '.join(l.strip() for l in rest_lines if l.strip())
            if continuation:
                desc = (desc + ' ' + continuation).strip()
            return potential_type, desc

    all_lines = [stripped] + [l.strip() for l in rest_lines if l.strip()]
    return None, ' '.join(all_lines).strip()


def parse_google(text: str) -> ParsedDocstring:
    """Parse a Google-style docstring into a ParsedDocstring."""
    doc = ParsedDocstring(original_style=DocstringStyle.GOOGLE)

    if not text.strip():
        return doc

    lines = text.split('\n')

    base_indent = 0
    for line in lines:
        if line.strip():
            base_indent = _get_indent(line)
            break

    sections = []
    pre_section_lines = []
    current_section = None
    current_body = []

    for line in lines:
        if not line.strip():
            if current_section is not None:
                current_body.append(line)
            else:
                pre_section_lines.append(line)
            continue

        line_indent = _get_indent(line)
        m = SECTION_RE.match(line)

        if m and line_indent == base_indent:
            section_name = m.group(2).strip()
            if section_name in GOOGLE_SECTION_HEADERS:
                if current_section is not None:
                    sections.append((current_section, current_body))
                current_section = section_name
                current_body = []
                continue

        if current_section is not None:
            current_body.append(line)
        else:
            pre_section_lines.append(line)

    if current_section is not None:
        sections.append((current_section, current_body))

    _parse_pre_section(pre_section_lines, doc)

    for title, body in sections:
        _parse_section(title, body, doc)

    return doc


def _parse_pre_section(lines: list[str], doc: ParsedDocstring) -> None:
    """Parse pre-section text into summary and extended description."""
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return

    summary_lines = []
    rest_lines = []
    found_blank = False

    for line in lines:
        if not line.strip() and not found_blank:
            found_blank = True
            rest_lines.append(line)
        elif found_blank:
            rest_lines.append(line)
        else:
            summary_lines.append(line.strip())

    doc.summary = ' '.join(summary_lines).strip()

    if rest_lines:
        while rest_lines and not rest_lines[0].strip():
            rest_lines.pop(0)
        while rest_lines and not rest_lines[-1].strip():
            rest_lines.pop()
        if rest_lines:
            doc.extended_description = '\n'.join(l.strip() for l in rest_lines)


def _parse_section(title: str, body: list[str], doc: ParsedDocstring) -> None:
    """Parse a section and update the doc."""
    while body and not body[-1].strip():
        body.pop()

    if title in ('Args', 'Arguments', 'Parameters'):
        items = _parse_section_body(body, 0)
        for name, type_ann, desc in items:
            doc.params.append(ParamDoc(name=name, type_annotation=type_ann, description=desc))

    elif title in ('Returns', 'Return'):
        type_ann, desc = _parse_returns_body(body)
        doc.returns = ReturnsDoc(type_annotation=type_ann, description=desc)

    elif title in ('Yields', 'Yield'):
        type_ann, desc = _parse_returns_body(body)
        doc.yields = YieldsDoc(type_annotation=type_ann, description=desc)

    elif title in ('Raises', 'Raise'):
        items = _parse_section_body(body, 0)
        for name, _, desc in items:
            doc.raises.append(RaisesDoc(exc_type=name, description=desc))

    else:
        content_lines = []
        for line in body:
            content_lines.append(line.rstrip())
        non_empty = [l for l in content_lines if l.strip()]
        if non_empty:
            min_indent = min(_get_indent(l) for l in non_empty)
            content_lines = [l[min_indent:] if l.strip() else '' for l in content_lines]
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        doc.custom_sections.append(SectionDoc(title=title, content='\n'.join(content_lines)))
