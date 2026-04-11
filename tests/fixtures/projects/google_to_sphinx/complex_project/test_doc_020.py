# SPDX-License-Identifier: MIT
"""NodeFlow — Python/JS pair for exit resolution =============================================

Single responsibility: resolve a node's exit.options (and optional choice key)
into the next target. Python holds no policy; it only bridges to JS and
normalizes outputs. The logic lives in `game/scripting/defaults/node_flow.js`.

Why a separate class?
---------------------
EventGraph owns traversal/state/analytics. Exit selection is a distinct
concern and has its own replacement/modding surface. Keeping NodeFlow separate
lets us evolve branching policy without touching traversal code.

JS contract (node_flow.js)
--------------------------
Must define global functions:
- `resolve_choice(ctx)` -> `{ state_updates:{ vars:{ next_node_id?, next_cluster_id?, end? } } }
- `resolve_next(ctx)`   -> `{ state_updates:{ vars:{ next_node_id?, next_cluster_id?, end? } } }`

Python API
---------
nf = NodeFlow()
out = nf.resolve_choice(options, choice_key, node_id='N1')
# out is a dict: { 'next_node_id': str|None, 'next_cluster_id': str|None, 'end': bool }

Tests should cover:
- map and array options
- to_cluster and end flags
- absence of hooks (graceful defaults)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from game.scripting.engine_js import JSEngine
from game.scripting.engine_lua import LuaEngine
from game.scripting.types import Context, State, PluginManifest
from labyrinth.domain.settings import Settings  # local import to avoid optional dependency at import time


DEFAULTS_DIR = Path(__file__).parent / "scripting" / "defaults"
DEFAULT_JS = DEFAULTS_DIR / "node_flow.js"
DEFAULT_LUA = DEFAULTS_DIR / "node_flow.lua"


class NodeFlow:
    """Bridge to JS node exit resolution.

    This class loads `node_flow.js` and exposes two typed helpers that return a
    normalized Python dict with the canonical triplet: `next_node_id`,
    `next_cluster_id`, and `end`.
    """
    pass
