"""Parse Sphinx-style docstrings into ParsedDocstring."""
from __future__ import annotations
import re
from typing import Optional
from pydocstring.models import (
    ParsedDocstring, ParamDoc, RaisesDoc, ReturnsDoc, YieldsDoc,
    SectionDoc, DocstringStyle,
)
from pydocstring.parser_google import _parse_section

FIELD_RE = re.compile(r'^\s*:(\w+)(?:\s+(\S+(?:\s+\S+)*?))?:\s*(.*)')

SIMPLE_FIELD_RE = re.compile(r'^\s*:(returns?|rtype|yields?):\s*(.*)')

GOOGLE_SECTION_RE = re.compile(r'^(\s*)([A-Z][a-zA-Z ]*?):\s*$')

GOOGLE_SECTION_HEADERS = {
    'Args', 'Arguments', 'Parameters', 'Returns', 'Return', 'Yields', 'Yield',
    'Raises', 'Raise', 'Note', 'Notes', 'Example', 'Examples', 'Warning',
    'Warnings', 'Todo', 'See Also', 'References', 'Attributes',
}


def _get_indent(line: str) -> int:
    """Return the number of leading spaces in *line*."""
    return len(line) - len(line.lstrip())


def parse_sphinx(text: str) -> ParsedDocstring:
    """Parse a Sphinx-style docstring into a ParsedDocstring."""
    doc = ParsedDocstring(original_style=DocstringStyle.SPHINX)

    if not text.strip():
        return doc

    lines = text.split('\n')

    pre_field_lines = []
    field_lines = []
    in_fields = False

    for line in lines:
        stripped = line.strip()
        if not in_fields:
            if FIELD_RE.match(line) or SIMPLE_FIELD_RE.match(line):
                in_fields = True
                field_lines.append(line)
            elif GOOGLE_SECTION_RE.match(line) and stripped.rstrip(':') in GOOGLE_SECTION_HEADERS:
                in_fields = True
                field_lines.append(line)
            else:
                pre_field_lines.append(line)
        else:
            field_lines.append(line)

    _parse_pre_field(pre_field_lines, doc)
    _parse_fields(field_lines, doc)

    return doc


def _parse_pre_field(lines: list[str], doc: ParsedDocstring):
    """Parse pre-field text into summary and extended description."""
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


def _parse_fields(lines: list[str], doc: ParsedDocstring):
    """Parse sphinx field list and google custom sections."""
    if not lines:
        return

    fields = []
    google_sections = []

    current_field_key = None
    current_field_arg = None
    current_content_lines = []
    in_google_section = False
    current_google_title = None
    current_google_body = []

    for line in lines:
        stripped = line.strip()

        m = FIELD_RE.match(line)
        if m:
            if in_google_section:
                google_sections.append((current_google_title, current_google_body))
                in_google_section = False
                current_google_title = None
                current_google_body = []
            elif current_field_key is not None:
                fields.append((current_field_key, current_field_arg, current_content_lines))

            current_field_key = m.group(1)
            current_field_arg = m.group(2)
            content = m.group(3).strip()
            current_content_lines = [content] if content else []
            continue

        gm = GOOGLE_SECTION_RE.match(line)
        if gm and gm.group(2).strip() in GOOGLE_SECTION_HEADERS:
            if in_google_section:
                google_sections.append((current_google_title, current_google_body))
            elif current_field_key is not None:
                fields.append((current_field_key, current_field_arg, current_content_lines))
                current_field_key = None
                current_field_arg = None
                current_content_lines = []

            in_google_section = True
            current_google_title = gm.group(2).strip()
            current_google_body = []
            continue

        if in_google_section:
            current_google_body.append(line)
        elif current_field_key is not None:
            current_content_lines.append(stripped)

    if in_google_section:
        google_sections.append((current_google_title, current_google_body))
    elif current_field_key is not None:
        fields.append((current_field_key, current_field_arg, current_content_lines))

    type_map: dict[str, str] = {}
    rtype = None

    for key, arg, content_lines in fields:
        content = ' '.join(content_lines).strip()
        key_lower = key.lower()

        if key_lower == 'type' and arg:
            type_map[arg] = content
        elif key_lower == 'rtype':
            rtype = content

    processed_params: dict[str, ParamDoc] = {}
    returns_desc = None
    yields_desc = None

    for key, arg, content_lines in fields:
        content = ' '.join(content_lines).strip()
        key_lower = key.lower()

        if key_lower == 'param':
            if arg:
                parts = arg.split()
                if len(parts) >= 2:
                    param_type = ' '.join(parts[:-1])
                    param_name = parts[-1]
                else:
                    param_name = parts[0]
                    param_type = type_map.get(param_name)

                if param_name not in processed_params:
                    processed_params[param_name] = ParamDoc(
                        name=param_name,
                        type_annotation=param_type,
                        description=content,
                    )
                else:
                    processed_params[param_name].description = content
                    if param_type:
                        processed_params[param_name].type_annotation = param_type

        elif key_lower == 'type' and arg:
            if arg in processed_params:
                processed_params[arg].type_annotation = content
            else:
                processed_params[arg] = ParamDoc(name=arg, type_annotation=content)

        elif key_lower in ('returns', 'return'):
            returns_desc = content

        elif key_lower == 'rtype':
            pass

        elif key_lower in ('raises', 'raise'):
            exc_type = arg or ''
            doc.raises.append(RaisesDoc(exc_type=exc_type, description=content))

        elif key_lower in ('yields', 'yield'):
            yields_desc = content

    for param in processed_params.values():
        if param.name not in [p.name for p in doc.params]:
            doc.params.append(param)

    if returns_desc is not None or rtype is not None:
        doc.returns = ReturnsDoc(
            type_annotation=rtype,
            description=returns_desc or '',
        )

    if yields_desc is not None:
        doc.yields = YieldsDoc(description=yields_desc)

    for title, body in google_sections:
        _parse_section(title, body, doc)
