from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from .settings import Settings


logger = logging.getLogger("LegendGame")

@dataclass(frozen=True)
class AssetGroup:
    """Configuration for a group of related assets.

    Attributes:
        directory: Base directory path relative to local root
        file_format: Default file extension for files in this group (e.g., 'png', 'ogg')
    """
    pass


class AssetLocator:
    """Resolve asset directories and files based on settings.json.

    Rules:
    - All assets are expected to exist under Settings.default_local_path()/<directory>
    - No fallback to project repository paths; callers must ensure deployment.
    - file_format is a group-specific default extension (png/ogg/wav).
    """
    pass


__all__ = ["AssetLocator", "AssetGroup"]
