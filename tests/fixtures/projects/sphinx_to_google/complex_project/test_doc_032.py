"""[Mock] remove-voiceover: verify IO and overwrite rules with fake FS

Simulates a small filesystem in memory to verify that:
- Input files are read
- Output files are written to expected paths with voiceover removed
- Overwrite respects --force
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import pytest

from pipelines.voice.actions.remove_voiceover import RemoveVoiceoverOperation
from pipelines.voice.services import ServiceBundle
from pipelines.voice.validation import RemoveVoiceoverConfig
from pipelines.voice.io.filesystem import IFileSystem


class _CaptureFS(IFileSystem):
    """Minimal in-memory filesystem for text files used by mock tests.

    Provides just enough behavior to simulate reading and writing JSON files
    without touching the real disk. Directory semantics are approximated.
    """

    def __init__(self, files: Optional[Dict[Path, str]] = None):
        """Initialize with an optional mapping of file paths to contents.

        :param files: Initial files dictionary (path -> text content)
        :type files: Dict[pathlib.Path, str] | None
        """
        pass

    def exists(self, path: Path) -> bool:  # type: ignore[override]
        """Return True if the path exists (file or directory)."""
        pass

    def is_file(self, path: Path) -> bool:  # type: ignore[override]
        """Return True if the path is a file."""
        pass

    def is_dir(self, path: Path) -> bool:  # type: ignore[override]
        """Return True if the path is a directory."""
        pass

    def iterdir(self, path: Path):  # type: ignore[override]
        """Yield direct children to simulate a non-empty directory."""
        pass

    def read_text(self, path: Path, encoding: str = "utf-8") -> str:  # type: ignore[override]
        """Read and return text contents of a file."""
        pass

    def write_text(self, path: Path, data: str, encoding: str = "utf-8"):  # type: ignore[override]
        """Write text data to a file, creating parent directory if needed."""
        pass

    def read_bytes(self, path: Path) -> bytes:  # type: ignore[override]
        """Read bytes from a file (backed by stored text)."""
        pass

    def write_bytes(self, path: Path, data: bytes):  # type: ignore[override]
        """Write bytes to a file (stored as text)."""
        pass

    def mkdir(self, path: Path, parents: bool = False, exist_ok: bool = False):  # type: ignore[override]
        """Create a directory path."""
        pass

    def remove_tree(self, path: Path):  # type: ignore[override]
        """Recursively remove files and dirs under path."""
        pass

    def move(self, src: Path, dst: Path):  # type: ignore[override]
        """Move/rename a file path."""
        pass

    def rename(self, src: Path, dst: Path):  # type: ignore[override]
        """Alias to :meth:`move`."""
        pass

    def copy_tree(self, src: Path, dst: Path):  # type: ignore[override]
        """Not implemented for this test filesystem."""
        pass


def _make_services(fs: IFileSystem) -> ServiceBundle:
    """Create a ServiceBundle with the provided filesystem."""
    pass  # type: ignore[arg-type]


def test_mock_writes_cleaned_output_and_preserves_fields():
    """
    [Mock] remove-voiceover: writes cleaned output and preserves other fields.

    Scenario:
      - Provide a simple script with two dialogue entries.
      - Run the operation and assert the output has no 'voiceover' fields.

    Boundaries:
      - Uses in-memory filesystem to avoid real disk I/O.

    On failure, first check:
      - That the output path was written and contains valid JSON.
    """
    pass


def test_mock_overwrite_requires_force():
    """
    [Mock] remove-voiceover: overwrite behavior with --force.

    Scenario:
      - Output file pre-exists; run operation with force=True.
      - Expect output to be overwritten successfully.

    Boundaries:
      - In-memory filesystem models pre-existing output.

    On failure, first check:
      - That the output file contents changed after the run.
    """
    pass
