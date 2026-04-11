"""Helper utilities for loading and calling JavaScript in tests."""

import json
from typing import Any, List

from game.scripting.engine_js import JSEngine
from game.scripting.types import PluginManifest


def load_js(
    engine: JSEngine,
    code: str,
    *,
    entry_file: str,
    plugin_id: str,
    capabilities: List[str]
):
    """
    Load JavaScript code into a JSEngine instance.
    
    :param engine: JSEngine instance to load code into
    :param code: JavaScript source code
    :param entry_file: Name of the entry file (for manifest)
    :param plugin_id: Unique plugin identifier
    :param capabilities: List of capability strings
    """
    pass


def call_js_json(engine: JSEngine, fn: str, *args: Any) -> Any:
    """
    Call a JavaScript function with Python arguments and parse JSON result.
    
    The JS function should expect JSON-encoded string arguments.
    
    :param engine: JSEngine instance with loaded code
    :param fn: Function name to call
    :param args: Positional arguments (will be JSON-encoded and escaped)
    :returns: Parsed JSON result
    """
    pass
