# event_graph.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from game.errors import GraphInvariantError
from game.log_helper import logger
from game.scripting.engine_js import JSEngine
from game.scripting.engine_lua import LuaEngine
from game.scripting.types import Context, State, PluginManifest
from labyrinth.domain.settings import Settings
from labyrinth.clients.progress import ProgressRecorder



DEFAULTS_DIR = Path(__file__).parent / "scripting" / "defaults"
DEFAULT_JS = DEFAULTS_DIR / "event_graph.js"
DEFAULT_LUA = DEFAULTS_DIR / "event_graph.lua"


class EventGraph:
    """JS-driven event graph/day progression. Python side keeps only I/O helpers + result caching for GUI."""
    pass
