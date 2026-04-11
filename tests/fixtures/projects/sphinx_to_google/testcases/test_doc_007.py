"""
A module providing network download services, including real and dry-run implementations.

This module contains an abstract base class for download services, a concrete download
service with progress and integrity checks, and a dry-run implementation for logging
download actions without execution.

* :class: `IDownloadService` - abstract base class for download services.
* :class: `RealDownloadService` - real network download service with progress and integrity checks.
* :class: `DryRunDownloadService` - logging-only download service used for dry-run modes.
"""

from __future__ import annotations

import urllib.error
from pathlib import Path
from time import monotonic
from typing import Optional
from urllib.request import urlopen

from pipelines.voice.utils.log_helper import logger


class IDownloadService:
    """Abstract network download service."""

    def download(self, url: str, dest: Path):
        """Download a URL into `dest`, overwriting if it exists."""
        pass


class RealDownloadService(IDownloadService):
    """Real network download service with progress and integrity checks."""

    def download(self, url: str, dest: Path):
        """Download URL to dest with a simple text progress bar.

        - Uses Content-Length (if available) to compute percentage and MB totals.
        - If the final size is less than Content-Length, treats it as a fatal error:
          deletes the partial file and raises OSError.
        - Logs total download time in both success and failure cases.
        """
        pass

    @staticmethod
    def download_progress_bar(dest: Path, downloaded: int, expected_bytes: Optional[int], start: float, url: str) -> Optional[tuple[int, int]]:
        """
        Downloads a file from a given URL to a destination path and displays a progress bar
        during the download process. Handles network or filesystem errors gracefully, attempts
        to clean up partially downloaded files if an error occurs, and provides logging of download
        progress and any issues encountered.

        :param dest: Destination path where the downloaded file will be saved.
        :type dest: Path
        :param downloaded: The initial number of bytes already downloaded (if any).
        :type downloaded: int
        :param expected_bytes: The total expected size of the file in bytes, if known.
        :type expected_bytes: Optional[int]
        :param start: Start time for tracking download elapsed time.
        :type start: float
        :param url: The URL from which the file will be downloaded.
        :type url: str
        :return: A tuple containing the total bytes downloaded and the expected file size in bytes (if available).
        :rtype: Optional[tuple[int, int]]
        """
        pass


class NullDownloadService(IDownloadService):
    """Dry-run download service that logs without downloading."""

    def download(self, url: str, dest: Path):
        """Log the download action without performing it."""
        pass
