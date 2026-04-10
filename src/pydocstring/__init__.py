"""PyDocstring - Convert Python docstrings between Google and Sphinx styles."""

from pydocstring.converter import convert_file, convert_project, detect_docstring_style
from pydocstring.project_scanner import scan_project
from pydocstring.models import (
    DocstringStyle,
    ParsedDocstring,
    ParamDoc,
    RaisesDoc,
    ReturnsDoc,
    YieldsDoc,
    SectionDoc,
    StyleDetectionResult,
    FileConversionResult,
    ProjectConversionResult,
    PythonFileInfo,
)

__all__ = [
    "convert_file",
    "convert_project",
    "detect_docstring_style",
    "scan_project",
    "DocstringStyle",
    "ParsedDocstring",
    "ParamDoc",
    "RaisesDoc",
    "ReturnsDoc",
    "YieldsDoc",
    "SectionDoc",
    "StyleDetectionResult",
    "FileConversionResult",
    "ProjectConversionResult",
    "PythonFileInfo",
]
