"""Plugin loader for discovering and loading script plugins."""

import json
from pathlib import Path
from typing import Tuple, List

from game.scripting.types import PluginManifest
from game.scripting.errors import ManifestError
from game.scripting.engine_base import ScriptEngine
from game.scripting.engine_lua import LuaEngine
from game.scripting.engine_js import JSEngine
from game.log_helper import logger


def load_manifest(manifest_path: Path) -> PluginManifest:
    """
    Load and validate a plugin manifest.
    
    :param manifest_path: Path to manifest JSON file
    :returns: PluginManifest object
    :raises ManifestError: If manifest is invalid
    """
    pass


def load_plugin(manifest_path: Path) -> Tuple[PluginManifest, ScriptEngine]:
    """
    Load a plugin from its manifest.
    
    :param manifest_path: Path to manifest JSON file
    :returns: Tuple of (manifest, engine)
    :raises ManifestError: If manifest or script is invalid
    """
    pass


def discover_plugins(root_dir: Path) -> List[Path]:
    """
    Discover plugin manifests in a directory.
    
    :param root_dir: Root directory to search
    :returns: List of manifest paths
    """
    pass
