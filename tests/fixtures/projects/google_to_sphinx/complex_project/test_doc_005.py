#!/usr/bin/env python3
"""Deploy project assets to the user's local data directory.

Copies selected asset groups from the repository's "assets" tree to
~/.local/share/labyrinth/<relative-directory>, where relative-directory is
configured via settings.json (defaults exist).

Usage:
python tools/deploy_asset.py [--dry-run] [--verbose] [--clean]

Options:
--dry-run Show what would be copied without performing changes.
--verbose Print detailed file operations.
--clean Remove destination directories before copying.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple


def _project_root() -> Path:
        pass


def _prepare_sys_path():
        pass


_prepare_sys_path()

from labyrinth.domain.settings import Settings  # noqa: E402


@dataclass
class Plan:
    pass


def _iter_files(root: Path) -> Iterable[Path]:
        pass


def _copy_tree(src: Path, dst: Path, *, dry_run: bool, verbose: bool) -> int:
        pass


def _copy_file(src: Path, dst: Path, *, dry_run: bool, verbose: bool) -> int:
    """Copy a single file from src to dst (dst is the full target path, not a directory).

    Returns 1 if file copied (or would be copied in dry-run), 0 otherwise.
    """
    pass


def _compute_targets(settings: Settings) -> Tuple[Plan, Plan, Plan, Plan]:
    """Compute source and destination paths for asset deployment.

    Reads asset configuration from settings and constructs Plan objects
    for avatars, sound, fonts, and background image.

    Args:
        settings: Settings instance with asset configuration

    Returns:
        Tuple of (avatars_plan, sound_plan, fonts_plan, background_plan)
    """
    pass


def main(argv: list[str] | None = None) -> int:
    """Main entry point for asset deployment script.

    Parses command-line arguments and deploys configured asset groups from
    the repository to the user's local data directory.

    Args:
        argv: Optional command-line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    pass


if __name__ == "__main__":
    sys.exit(main())
