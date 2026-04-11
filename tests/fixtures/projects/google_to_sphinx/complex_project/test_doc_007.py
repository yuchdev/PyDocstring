# SPDX-License-Identifier: MIT
"""Emotions catalog with a thin JS bridge (logic lives in JS).

This module deliberately keeps Python *logic-free*: it stores emotion metadata
(a dict mapping emotion name -> {category, impact, emoji}) and offers
convenient accessors. Any *behavior* (e.g., normalization rules, tension
delta policy, mapping from emotion to social relation) is delegated to a
JavaScript file (`emotions.js`) so that mods can replace or extend it.

Default JS contract
-------------------
The default script must define these global functions:

- `init_emotions(ctxJson, emotionsJson) -> JSON string`
Optionally normalize/augment the provided emotions map. Should return a
JSON-encoded object (the possibly updated emotions map). If not defined,
Python keeps the original map.

- `normalize_emotion(ctxJson, label) -> JSON string`
Return a JSON-encoded `{"ok": true, "value": "<canonical>"}` if the label
can be normalized, otherwise `{"ok": false}`. Default behavior performs
exact match and case-insensitive fallback.

- `relation_from_emotion(ctxJson, name) -> JSON string`
Return a JSON-encoded `{"value": "friendly"|"neutral"|"hostile"}` indicating
the social relation implied by the emotion. Default uses the emotion's
`impact` field.

- `tension_delta(ctxJson, name) -> JSON string`
Return a JSON-encoded `{"value": <float>}` representing how this emotion
shifts group tension (e.g., positive emotions slightly reduce, negative
increase). Defaults: positive=-0.01, neutral=0.0, complex=+0.015, negative=+0.02.

This design allows modding the *policy* without touching Python code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, List
import quickjs

from game.log_helper import logger
from game.scripting.engine_js import JSEngine
from game.scripting.scripting_logging import ScriptingLogConfig

# TODO: `'scripting_log_dir' is not declared in __all__` - in what exactly __init__?
from game.log_helper import scripting_log_dir
from game.scripting.types import Context, State, PluginManifest
from game.errors import ValidationError

DEFAULTS_DIR = Path(__file__).parent / "scripting" / "defaults"
DEFAULT_EMOTIONS_JS = DEFAULTS_DIR / "emotions.js"


class Emotions:
    """Lightweight accessor around a mapping of emotion metadata with a JS bridge.

    The instance wraps an *in-memory* dictionary of emotion definitions and
    exposes common queries. Behavior is delegated to a JS script so that
    modders can change normalization or policy without touching Python.
    """
    pass
