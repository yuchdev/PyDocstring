"""Command-line interface for the scripting engine."""

from game.scripting.loader import load_manifest, load_plugin, discover_plugins
from game.scripting.errors import ManifestError, ScriptError
import sys
import json
from pathlib import Path
from typing import Optional

from game.scripting.types import Context, Exit, State


def cmd_validate(manifest_path: Path) -> int:
    """Validate a plugin manifest.
    
    :param manifest_path: Path to manifest file
    :returns: Exit code (0 for success)
    """
    pass


def cmd_run(manifest_path: Path, hook: str, ctx_path: Optional[Path]) -> int:
    """Run a plugin hook with a context.
    
    :param manifest_path: Path to manifest file
    :param hook: Hook name to call
    :param ctx_path: Path to context JSON file (optional)
    :returns: Exit code (0 for success)
    """
    pass


def cmd_list(root_dir: Path) -> int:
    """List plugins in a directory.
    
    :param root_dir: Root directory to search
    :returns: Exit code (0 for success)
    """
    pass


def main() -> int:
    """Main CLI entry point.
    
    :returns: Exit code
    """
    pass


if __name__ == "__main__":
    sys.exit(main())
