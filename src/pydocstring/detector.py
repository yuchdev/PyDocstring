"""Heuristic style detection for docstrings."""
from __future__ import annotations
import re
from pydocstring.models import DocstringStyle, StyleDetectionResult

GOOGLE_SECTION_HEADERS = {
    'Args', 'Arguments', 'Parameters', 'Returns', 'Return', 'Yields', 'Yield',
    'Raises', 'Raise', 'Note', 'Notes', 'Example', 'Examples', 'Warning',
    'Warnings', 'Todo', 'See Also', 'References', 'Attributes',
}

SPHINX_FIELD_PATTERN = re.compile(
    r'^\s*:(param|type|returns?|rtype|raises?|yields?|var|ivar)\b'
)

GOOGLE_SECTION_PATTERN = re.compile(
    r'^(\s*)([A-Z][a-zA-Z ]*?):\s*$'
)


def detect_style(text: str) -> StyleDetectionResult:
    """Detect the docstring style of the given text."""
    if not text.strip():
        return StyleDetectionResult(
            style=DocstringStyle.UNKNOWN,
            confidence=1.0,
            evidence=["Empty docstring"],
        )

    lines = text.split('\n')
    sphinx_count = 0
    google_count = 0
    evidence = []
    warnings = []

    for line in lines:
        if SPHINX_FIELD_PATTERN.match(line):
            sphinx_count += 1
            evidence.append(f"Sphinx field: {line.strip()[:50]}")

    for line in lines:
        m = GOOGLE_SECTION_PATTERN.match(line)
        if m:
            section_name = m.group(2).strip()
            if section_name in GOOGLE_SECTION_HEADERS:
                google_count += 1
                evidence.append(f"Google section: {section_name}")

    total = sphinx_count + google_count

    if total == 0:
        return StyleDetectionResult(
            style=DocstringStyle.UNKNOWN,
            confidence=0.6,
            evidence=["No style indicators found"],
        )

    if sphinx_count > 0 and google_count > 0:
        warnings.append("Docstring contains both Google and Sphinx style indicators")
        style = DocstringStyle.MIXED
        confidence = 0.7
    elif sphinx_count > 0:
        style = DocstringStyle.SPHINX
        confidence = min(1.0, 0.5 + sphinx_count * 0.1)
    else:
        style = DocstringStyle.GOOGLE
        confidence = min(1.0, 0.5 + google_count * 0.1)

    return StyleDetectionResult(
        style=style,
        confidence=confidence,
        evidence=evidence,
        warnings=warnings,
    )
