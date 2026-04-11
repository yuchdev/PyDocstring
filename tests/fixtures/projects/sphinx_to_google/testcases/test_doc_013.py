"""
Events runtime: validation and JS-driven semantics.

This module provides a thin, deterministic orchestration layer that:
  1) Validates authored event dictionaries against a declarative *metadata* contract.
  2) Delegates event semantics to a portable JavaScript hook
     `process_event(ctxJson, eventJson, metadataJson)`.
  3) Returns a flat list of *effects* (engine-agnostic dicts) that the host applies.

Design constraints:
- No assumptions about persistent event lists (pure, stateless calls).
- No JSON file I/O for data: callers pass Python dicts/lists already in memory.
- The only file read is the JS script that implements the semantics.
- No domain coupling (e.g., emotions) lives here; keep this layer generic.

Typical usage:

    # metadata defined by you
    from game.events.event import Events, EVENTS_METADATA

    # loads defaults/events.js
    runtime = Events(metadata_json=EVENTS_METADATA)

    # returns list[dict]
    effects = runtime.process_events(events_payload)
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from game.scripting.engine_js import JSEngine
from game.scripting.types import Context, State, PluginManifest
from game.log_helper import logger

# The default JS file should export: process_event(ctxJson, eventJson, metadataJson) -> JSON string
DEFAULTS_DIR = Path(__file__).parent / "scripting" / "defaults"
DEFAULT_JS = DEFAULTS_DIR / "events.js"


@dataclass
class EventMeta:
    """
    Optional per-event metadata carried alongside the core event.

    These fields are *advisory* for hosts and pipelines (ordering, tagging,
    provenance) and are **not** interpreted by this module.

    :param id: Stable authoring identifier or external reference.
    :param idx: Ordinal index within the input sequence (autofilled by validator).
    :param tags: Freeform labels for filtering or analytics.
    :param ts: Optional relative timestamp in milliseconds (authoring aid).
    :param node: Optional graph node identifier (e.g., storyboard link).
    :param source: Provenance marker (e.g., "handauthored", "genai", "plugin:xyz").
    """
    id: Optional[str] = None
    idx: Optional[int] = None
    tags: Optional[List[str]] = None
    ts: Optional[int] = None
    node: Optional[str] = None
    source: Optional[str] = None


class Events:
    """
    Validate events against a declarative contract and delegate semantics to JS.

    This class is intentionally *state-light*: it does not store or mutate
    event lists. Each method call operates on the input you provide and returns
    derived values (typed events or effects).

    The JavaScript file must export a single function with the signature::

        process_event(ctxJson, eventJson, metadataJson) -> JSON string

    where each argument is a JSON-encoded string, and the return value is a JSON
    string with an object like `{"effects": [...]}`. Effects are engine-agnostic
    dictionaries that your host system applies (e.g., "enter", "say", "env.set").

    :param metadata_json: Declarative contract specifying required/optional fields for each event type. Example:
                              {
                                  "enter": {"required_fields": ["character"], "optional_fields": []},
                                  "dialogue": {"required_fields": ["character","mood","text"], "optional_fields": ["to"]},
                                  ...
                              }
    :param js_script: Optional path to the JavaScript semantics file. If omitted, `defaults/events.js` is used.
    :raises TypeError: If `metadata_json` is not a dict.
    :raises FileNotFoundError: If the JS script path does not exist.
    :raises UnicodeDecodeError: If the JS file cannot be decoded as UTF-8.
    :raises Exception: Any error raised by the underlying JS engine load.
    """

    def __init__(self, metadata_json: Dict[str, Any], js_script: Optional[Path] = None):
        """Initialize the Events engine with metadata and optional custom JS script.

        Normalizes the metadata structure and loads the JavaScript validation/semantics
        engine for processing event payloads.

        Args:
            metadata_json: Event type metadata dictionary
            js_script: Optional path to a custom JavaScript semantics file

        Raises:
            TypeError: If metadata_json is not a dict
            FileNotFoundError: If the JS script path doesn't exist
            UnicodeDecodeError: If the JS file cannot be decoded
        """
        pass

    def validate_events(self, events_json: Any) -> Tuple[bool, List[Tuple[int, str]]]:
        """
        Validate an events payload against the metadata contract and aggregate errors.

        This validator does not `raise` for content errors; instead, it returns a tuple indicating validity
        and a list of offending item indexes with a human-readable description.

        Accepted containers:
          * list[dict] of events
          * dict with `events` (or `items`) -> list[dict]

        Validation rules (per item):
          * `event_type` must exist and be known (present in metadata).
          * All paths listed in `required_fields` must be present (supports dotted paths).
          * Optional fields are never enforced at this layer.

        Container-level errors (e.g., wrong shape) are reported with index `-1`.

        :param events_json: The events payload (list[dict] or dict with `events`/`items` list).
        :returns: `(is_valid, invalid_items)` where:
                  - `is_valid` is `True` if no errors were found,
                  - `invalid_items` is `list[ (index:int, message:str) ]` describing violations.
        """
        pass

    def process_event(self, event: Dict[str, Any], ctx_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a single event through the JS handler and return effects.

        This method validates the event, calls the JS `process_event` function,
        and extracts the effect array from the result.

        :param event: Event dictionary with at least `event_type` field.
        :param ctx_vars: Context variables to pass to JS (read-only snapshot).
        :returns: List of effect dictionaries.
        :raises ValueError: If the event is invalid.
        """
        pass

    def process_events(self, events_list: List[Dict[str, Any]], ctx_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a list of events and accumulate effects.

        This method processes events in order, accumulating effects. Invalid events
        are logged but do not stop processing.

        :param events_list: List of event dictionaries.
        :param ctx_vars: Context variables to pass to JS (read-only snapshot).
        :returns: The list of all accumulated effects from all events.
        """
        pass

    @staticmethod
    def _normalize_metadata(obj: Dict[str, Any]) -> Dict[str, Dict[str, List[str]]]:
        """
        Normalize the metadata dictionary.

        Lowercases event type keys and ensures each value has `required_fields` and
        `optional_fields` lists.

        :param obj: Raw metadata dictionary provided by the caller.
        :returns: Normalized metadata dictionary.
        :raises ValueError: If the metadata is not a mapping of event types to objects.
        """
        pass

    @staticmethod
    def _extract_items(events_json: Any) -> List[Dict[str, Any]]:
        """
        Extract the event list from a supported container.

        :param events_json: Either a list[dict] of events, or a dict with `events` or `items` list.
        :returns: The extracted list of event dicts.
        :raises ValueError: If no valid events array is found, or if elements are not dicts.
        """
        pass

    @staticmethod
    def _get_path(obj: Dict[str, Any], dotted: str) -> Any:
        """
        Resolve a dotted path within a nested dictionary.

        :param obj: The dictionary to traverse.
        :param dotted: Dotted path (e.g., `"payload.key"`).
        :returns: The value at that path, or `None` if any segment is missing.
        """
        pass
