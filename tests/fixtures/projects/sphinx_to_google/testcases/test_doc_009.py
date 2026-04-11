# SPDX-License-Identifier: MIT
"""
Emotions catalog with a thin JS bridge (logic lives in JS).

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
    """
    Lightweight accessor around a mapping of emotion metadata with a JS bridge.

    The instance wraps an *in-memory* dictionary of emotion definitions and
    exposes common queries. Behavior is delegated to a JS script so that
    modders can change normalization or policy without touching Python.
    """

    def __init__(self, emotions: Mapping[str, Mapping[str, str]], js_script: Optional[Path] = None):
        """
        Store a mutable copy of the dict users pass in (we never write to the caller's object)
        :param emotions: Mapping from emotion name to its metadata. Each value must
                         at least provide keys `category` and `impact`. An optional
                         `emoji` string is supported for UI.
        :param js_script: Optional path to a JS file implementing the default behavior.
                          If omitted, `defaults/emotions.js` is used.

        :raises FileNotFoundError: if the JS file path does not exist.
        :raises UnicodeDecodeError: if the JS file cannot be decoded as UTF-8.
        :raises Exception: if the JS engine fails to load the script.
        :raises ValidationError: if the emotion map is empty.
        """
        pass

    # ------------------------------- public API (data) -------------------------------

    def get_emotion_list(self) -> List[str]:
        """
        :returns: All emotion names (unordered).
        """
        pass

    def get_emotion_categories(self) -> List[str]:
        """
        :returns: Distinct `category` values present in the map.
        """
        pass

    def get_emotion_impacts(self) -> List[str]:
        """
        :returns: Distinct `impact` values present in the map.
        """
        pass

    def get_emotion_category(self, emotion: str) -> str:
        """
        :param emotion: Emotion key.
        :returns: Category string.
        :raises KeyError: If the emotion is unknown or lacks `category`.
        """
        pass

    def get_emotion_impact(self, emotion: str) -> str:
        """
        :param emotion: Emotion key.
        :returns: Impact string.
        :raises KeyError: If the emotion is unknown or lacks `impact`.
        """
        pass

    def get_emotion_emoji(self, emotion: str) -> str:
        """
        :param emotion: Emotion key.
        :returns: Emoji string for UI; rises if missing (intentional to surface authoring gaps).
        :raises KeyError: If the emotion is unknown or lacks `emoji`.
        """
        pass

    def list_by_category(self, category: str) -> List[str]:
        """
        :returns: Emotion names in the given category (empty if none).
        """
        pass

    def list_by_impact(self, impact: str) -> List[str]:
        """
        :returns: Emotion names with the given impact (empty if none).
        """
        pass

    def exists(self, label: str) -> bool:
        """
        :returns: True if an emotion with this exact key exists.
        """
        pass

    # ------------------------- public API (JS-delegated behavior) --------------------

    def normalize_emotion(self, label: str) -> Optional[str]:
        """
        Normalize a user/authored label to a canonical emotion key via JS rules.

        The default JS implementation first tries an exact match, then a
        case-insensitive match. Mods may implement synonyms or fuzzy logic.

        :param label: Authored/freeform label.
        :returns: Canonical key or `None` if normalization failed.
        """
        pass

    def relation_from_emotion(self, name: str) -> str:
        """
        Ask JS which social relation an emotion implies.

        Default: use the emotion's `impact` field.

        :param name: Canonical `emotion` key.
        :returns: "friendly" | "neutral" | "hostile"
        :raises KeyError: if the emotion is unknown and JS cannot resolve it.
        """
        pass

    def tension_delta(self, name: str) -> float:
        """
        Ask JS how this emotion should shift group tension.

        Default mapping (JS): positive=-0.01, neutral=0.0, complex=+0.015, negative=+0.02.

        :param name: Canonical `emotion` key.
        :returns: Float delta to *add* to the current tension.
        :raises KeyError: if the emotion is unknown and JS cannot resolve it.
        """
        pass

    # ------------------------------- internals --------------------------------------

    def _rebuild_indexes(self):
        """
        Rebuild category/impact reverse indexes from the current map.
        """
        pass

    def _encode(self, obj: Any) -> str:
        """
        Use engine's JSON encoder if available, else stdlib.
        """
        pass

    def _js_call_json(self, fn_name: str, *args: Any) -> Any:
        """
        Call a global JS function with arbitrary arguments and parse JSON result.

        :param fn_name: Global function name (e.g., 'normalize_emotion').
        :param args: Positional arguments (Python objects). They will be JSON-encoded.
        :returns: The parsed JSON value returned by the JS function; may be any type.
        :raises Exception: Surfaced from the JS engine if invocation fails.
        """
        pass
