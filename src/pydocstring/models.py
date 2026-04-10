"""Structured data models for docstring content representation."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class DocstringStyle(str, Enum):
    """Enumeration of supported docstring styles."""

    GOOGLE = "google"
    SPHINX = "sphinx"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class ParamDoc:
    """A documented parameter."""

    name: str
    type_annotation: Optional[str] = None
    description: str = ""


@dataclass
class RaisesDoc:
    """A documented exception."""

    exc_type: str
    description: str = ""


@dataclass
class ReturnsDoc:
    """Documented return value."""

    type_annotation: Optional[str] = None
    description: str = ""


@dataclass
class YieldsDoc:
    """Documented yield value."""

    type_annotation: Optional[str] = None
    description: str = ""


@dataclass
class SectionDoc:
    """A generic/custom section (e.g. Examples, Notes, etc.)."""

    title: str
    content: str = ""


@dataclass
class ParsedDocstring:
    """The fully parsed, structured representation of a docstring."""

    summary: str = ""
    extended_description: str = ""
    params: list[ParamDoc] = field(default_factory=list)
    returns: Optional[ReturnsDoc] = None
    yields: Optional[YieldsDoc] = None
    raises: list[RaisesDoc] = field(default_factory=list)
    custom_sections: list[SectionDoc] = field(default_factory=list)
    original_style: DocstringStyle = DocstringStyle.UNKNOWN


@dataclass
class StyleDetectionResult:
    """Result of style detection."""

    style: DocstringStyle
    confidence: float  # 0.0 to 1.0
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PythonFileInfo:
    """Info about a Python file found in a project scan."""

    path: Path
    relative_path: Path
    encoding: str = "utf-8"
    newline: str = "\n"


@dataclass
class FileConversionResult:
    """Result of converting a single file."""

    path: Path
    changed: bool = False
    original_source: str = ""
    converted_source: str = ""
    warnings: list[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class ProjectConversionResult:
    """Result of converting an entire project."""

    root: Path
    files_processed: int = 0
    files_changed: int = 0
    files_skipped: int = 0
    file_results: list[FileConversionResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
