"""Archiver provides basic ZIP archive operations.

* :class:`IArchiveService` - interface for archive operations.
* :class:`ZipArchiveService` - ZIP extraction/creation.
* :class:`NullArchiveService` - logging-only archive service used for dry-run modes.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
import py7zr

from pipelines.voice.utils.log_helper import logger


class IArchiveService:
    """Abstract archive / zip operations."""

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> Path:
        """Extract a ZIP archive and return the root of extracted content."""
        pass  # pragma: no cover

    def create_zip(self, src_dir: Path, zip_path: Path):
        """Create a ZIP file from directory `src_dir`."""
        pass  # pragma: no cover


class ZipArchiveService(IArchiveService):
    """ZIP implementation based on :mod:`zipfile`."""

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> Path:
        """Extract ZIP into `dest_dir` and return top-level extracted dir.

        If the archive creates a single top-level directory, that directory
        is returned. Otherwise, `dest_dir` is returned.
        """
        pass

    def create_zip(self, src_dir: Path, zip_path: Path):
        """Create a flat ZIP archive from all direct children of `src_dir`."""
        pass


class P7ZipArchiveService(IArchiveService):
    """7z-based archive service using the `py7zr` Python package.

    - `extract_zip(zip_path, dest_dir)` extracts into `dest_dir` and returns the top-level
      extracted directory if the archive produced a single directory, otherwise returns `dest_dir`.
    - `create_zip(src_dir, zip_path)` creates a 7z archive containing the direct children of `src_dir`.
      If `src_dir` is empty, an empty 7z archive is created.
    """

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> Path:
        """
        Extracts the contents of a 7z archive to a specified destination directory.

        The method ensures the destination directory exists and extracts all files
        from the given 7z archive. If the extracted archive contains a single
        top-level folder, the path to that folder is returned. Otherwise, the path
        to the destination directory is returned.

        :param zip_path: The path to the 7z archive to be extracted.
        :type zip_path: Path
        :param dest_dir: The destination directory where the archive content will
            be extracted.
        :type dest_dir: Path
        :return: The path to the top-level folder from the extracted archive if
            it contains a single directory, otherwise the path to the destination
            directory.
        :rtype: Path
        :raises OSError: If the extraction process fails due to a bad archive,
            missing password, general archive error, or I/O disturbance.
        """
        pass

    def create_zip(self, src_dir: Path, zip_path: Path):
        """
        Creates a 7z archive containing the contents of the source directory at the specified
        destination.

        This function zips the contents of the provided source directory into a .7z archive
        at the given destination path. It ensures the parent directory of the destination
        exists and handles situations where the source directory is empty by creating an
        empty archive.

        :param src_dir: The path to the source directory to be archived.
        :type src_dir: Path
        :param zip_path: The path where the 7z archive should be created.
        :type zip_path: Path
        :raises OSError: If there is an error during archive creation or I/O issues.
        """
        pass


class NullArchiveService(IArchiveService):
    """Dry-run archive service that logs without performing actions."""

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> Path:
        """Log the extraction action without performing it."""
        pass

    def create_zip(self, src_dir: Path, zip_path: Path):
        """Log the ZIP creation action without performing it."""
        pass
