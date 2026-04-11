# group.py
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Set

from game.character import Character
from game.emotions import Emotions
from game.errors import DuplicateAliasError, UnknownCharacterError
from game.log_helper import logger
from game.scripting.types import Context, State


class Group:
    """
    Container for potential and active characters with JS-owned group dynamics.

    Owns:
      - a registry of Character objects keyed by canonical name,
      - an ordered active roster (`Active`),
      - a case-sensitive alias map (alias -> canonical).

    Python holds only durable data and performs data exchange with the JS engine.
    All gameplay/social logic happens in JS. Python applies only membership/control
    effects (enter/leave/control.*) requested by JS.

    :param emotions: Global Emotions instance (used when constructing Character).
    :param characters: Optional map name -> stats to seed/merge characters.
    """

    class GroupDynamics:
        """
        Thin view over the Group.active roster + a JS-owned state bucket.

        - No gameplay logic here. JS decides everything and mutates through bridges.
        - Membership is delegated to Group (single source of truth).
        - `state` and `history` are opaque bags the JS layer controls.
        """

        def __init__(self, characters: Group, *, group_id: str = "default"):
            """Initialize the ActiveGroup view over the Group roster.

            Creates a lightweight wrapper that delegates membership operations to the
            underlying Group while maintaining JS-controlled state and history.

            Args:
                characters: The Group instance to wrap
                group_id: Identifier for this active group (default "default")
            """
            pass   # JS-owned event/dialog log entries

        # Membership pass-through
        def add(self, name_or_alias: str):
            """
            Add a member to the active roster.

            :param name_or_alias: Canonical name or registered alias.
            :type name_or_alias: str
            :raises UnknownCharacterError: If the name/alias cannot be resolved.
            """
            pass

        def remove(self, name_or_alias: str):
            """
            Remove a member from the active roster.

            :param name_or_alias: Canonical name or registered alias.
            :type name_or_alias: str
            :raises UnknownCharacterError: If the name/alias cannot be resolved.
            """
            pass

        def clear(self):
            """
            Remove all members from the active roster.
            """
            pass

        # Queries
        def contains(self, name_or_alias: str) -> bool:
            """
            Check membership in the active roster.

            :param name_or_alias: Canonical name or registered alias.
            :type name_or_alias: str
            :returns: True if the resolved character is active, False otherwise.
            :rtype: bool
            :raises UnknownCharacterError: If the name/alias cannot be resolved.
            """
            pass

        def names(self) -> List[str]:
            """
            Get ordered canonical names of active members.

            :returns: Ordered list of canonical names.
            :rtype: list[str]
            """
            pass

        def members(self) -> List[Character]:
            """
            Get Character objects for active members in order.

            :returns: Ordered list of Character objects.
            :rtype: list[Character]
            """
            pass

        def __iter__(self) -> Iterator[Character]:
            """
            Iterate over active members as Character objects (in order).

            :returns: Iterator of Character instances.
            :rtype: Iterator[Character]
            """
            pass

    @dataclass
    class Active:
        """
        Ordered roster of active characters (membership/order only, logic-free).

        Stores canonical names internally; provides views to Character objects.
        """

        owner: "Group"
        order: List[str] = field(default_factory=list)
        set: Set[str] = field(default_factory=set)

        def add(self, name: str):
            """
            Activate a character by canonical name.

            :param name: Canonical character name.
            :type name: str
            :raises UnknownCharacterError: If the character is unknown.
            """
            pass

        def remove(self, name: str):
            """
            Deactivate a character by canonical name (no-op if absent).

            :param name: Canonical character name.
            :type name: str
            """
            pass

        def clear(self):
            """
            Remove all active members.
            """
            pass

        def contains(self, name: str) -> bool:
            """
            Check if a canonical name is active.

            :param name: Canonical character name.
            :type name: str
            :returns: True if active, False otherwise.
            :rtype: bool
            """
            pass

        def names(self) -> List[str]:
            """
            Return ordered canonical names of active members.

            :returns: Ordered list of canonical names.
            :rtype: list[str]
            """
            pass

        def characters(self) -> List[Character]:
            """
            Return Character objects corresponding to active members.

            :returns: Ordered list of Character instances.
            :rtype: list[Character]
            """
            pass

        def __iter__(self) -> Iterator[Character]:
            """
            Iterate over active characters as Character objects (in order).

            :returns: Iterator of Character instances.
            :rtype: Iterator[Character]
            """
            pass

    def __init__(self, emotions: Emotions, characters: Optional[Mapping[str, Mapping[str, Any]]], js_engine: Optional[Any] = None):
        """
        Initialize the Group container.
        :param emotions: Emotions catalog instance.
        :param characters: Optional mapping of character names to stats.
        :param js_engine: Optional JS engine for group dynamics callbacks.
        """
        pass

    def upsert_from_characters_map(self, characters: Mapping[str, Mapping[str, Any]]):
        """
        Insert or update many characters from `characters`
        """
        pass

    def upsert(self, name: str, character: Mapping[str, Any]) -> Character:
        """
        Insert or update a single character (bag-first, logic-free).

        :param str name: Canonical character name.
        :param Mapping[str, Any] character: Attribute map to merge (required).
        :returns: The created or updated `Character` instance.
        """
        pass

    def rename(self, current_name: str, new_name: str):
        """
        Rename a canonical character key (no logic). Updates registry, active roster,
        and any aliases pointing to the old name.
        """
        pass

    def remove(self, name_or_alias: str):
        """
        Remove character from the registry and active roster; clean control + aliases.
        """
        pass

    def _bootstrap_aliases_from_registry(self):
        """
        Initialize `_aliases` from characters' self-reported aliases.
        """
        pass

    def register_alias(self, alias: str, canonical: str):
        """
        Register or confirm an alias for a canonical name.

        :param alias: Alias to register (case-sensitive).
        :type alias: str
        :param canonical: Canonical character name to map to.
        :type canonical: str
        :raises UnknownCharacterError: If the canonical name is unknown.
        :raises DuplicateAliasError: If the alias points to a different canonical name.
        """
        pass

    def unregister_alias(self, alias: str):
        """
        Remove an alias mapping if present.

        :param alias: Alias to remove.
        :type alias: str
        """
        pass

    def resolve(self, name_or_alias: str) -> str:
        """
        Resolve a canonical name from a canonical or alias.
        """
        pass

    def has(self, name_or_alias: str) -> bool:
        """
        Return whether a canonical name or alias exists in the registry.

        :param name_or_alias: Canonical name or registered alias.
        :type name_or_alias: str
        :returns: True if resolvable, False otherwise.
        :rtype: bool
        """
        pass

    def get(self, name_or_alias: str) -> Character:
        """
        Get a Character by canonical name or alias.

        :param name_or_alias: Canonical name or registered alias.
        :type name_or_alias: str
        :returns: Character instance for the resolved canonical name.
        :rtype: Character
        :raises UnknownCharacterError: If the name/alias cannot be resolved.
        """
        pass

    def names(self) -> List[str]:
        """
        List canonical names of all registered characters.

        :returns: Unordered list of canonical names.
        :rtype: list[str]
        """
        pass

    def characters(self) -> List[Character]:
        """
        List Character objects for all registered characters.

        :returns: Unordered list of Character instances.
        :rtype: list[Character]
        """
        pass

    def activate(self, name_or_alias: str):
        """
        Activate a character by canonical name or alias.

        :param name_or_alias: Canonical name or registered alias to activate.
        :type name_or_alias: str
        :raises UnknownCharacterError: If the name/alias cannot be resolved.
        """
        pass

    def deactivate(self, name_or_alias: str):
        """
        Deactivate a character by canonical name or alias.

        :param name_or_alias: Canonical name or registered alias to deactivate.
        :type name_or_alias: str
        :raises UnknownCharacterError: If the name/alias cannot be resolved.
        """
        pass

    def is_active(self, name_or_alias: str) -> bool:
        """
        Check whether a character is active.

        :param name_or_alias: Canonical name or registered alias.
        :type name_or_alias: str
        :returns: True if the character is active, False otherwise.
        :rtype: bool
        :raises UnknownCharacterError: If the name/alias cannot be resolved.
        """
        pass

    def set_control(self, name_or_alias: str, mode: str):
        """Set control routing (e.g., 'ai' or 'user'); 'script' is implied when absent."""
        pass

    def get_control(self, name_or_alias: str) -> str:
        """
        Get the current control routing for a character.

        :param name_or_alias: Canonical name or registered alias.
        :type name_or_alias: str
        :returns: "ai", "user", or "script" if not explicitly set.
        :rtype: str
        :raises UnknownCharacterError: If the name/alias cannot be resolved.
        """
        pass

    def to_character_map(self, only_active: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Export a mapping of name -> full attribute bag.
        """
        pass

    def active_group_snapshot(self) -> List[Dict[str, Any]]:
        """
        Return ordered, read-only snapshots for all active characters.

        Each item matches Character.as_group_snapshot(); this is not gameplay logic,
        just structured access to the data JS has set.
        """
        pass

    def relation_matrix(self, *, only_active: bool = True, fill_missing: bool = False) -> Dict[str, Dict[str, str]]:
        """
        Build a read-only view of relation impacts (as-is, no derivation).
        If `fill_missing` is False, pairs without explicit impact are omitted.

        :param only_active: Limit matrix to active roster members.
        :param fill_missing: If True, add 'neutral' for missing pairs (optional).
        """
        pass

    def apply_effects(self, effects: Sequence[Mapping[str, Any]]) -> int:
        """
        Apply roster/control effects emitted by JS (no other kinds handled here).

        Handles:
          - enter:          {"type": "enter", "character": "<name>"}
          - leave:          {"type": "leave", "character": "<name>"}
          - control.ai:     {"type": "control.ai", "character": "<name>"}
          - control.user:   {"type": "control.user", "character": "<name>"}
          - control.return: {"type": "control.return", "character": "<name>"}

        :returns: Count of applied effects.
        :raises UnknownCharacterError: If an effect references an unknown character.
        """
        pass

    def on_line(self, *, speaker: str, text: str, mood: str, to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Notify JS about a new dialogue line to update group dynamics.

        :param speaker: Canonical character name who spoke.
        :param text: Line text.
        :param mood: Emotion/mood of the line.
        :param to: Optional target character(s).
        :returns: List of effects to apply.
        """
        pass

    def apply_group_effects(self, effects: Sequence[Mapping[str, Any]]) -> int:
        """
        Apply group-related effects returned by JS.

        Handles:
          - group.enter/leave/clear: roster changes (delegates to activate/deactivate)
          - group.set_tension: set tension value (clamped 0..1)
          - group.adjust_tension: adjust tension by delta (clamped 0..1)
          - group.set_mood: set dominant mood
          - group.mood_histogram.patch: merge histogram updates
          - group.history.add: add history entry (bounded)
          - group.state.patch: opaque state merge

        :param effects: List of effect dictionaries.
        :returns: Count of applied effects.
        """
        pass

    def _apply_group_effects(self, result: Optional[Dict[str, Any]]):
        """
        Internal helper to apply group state updates from JS result.

        :param result: JS result dictionary with optional state_updates.vars.group.
        """
        pass

    def group_snapshot(self) -> Dict[str, Any]:
        """
        Return a snapshot of the group state for external consumption.

        :returns: Dictionary with active roster and group state.
        """
        pass
