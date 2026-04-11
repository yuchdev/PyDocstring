"""Type definitions for the scripting engine."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Protocol


@dataclass(frozen=True)
class Exit:
    """
    Represents an exit option from a dialog node.
    """
    
    id: str
    weight: float = 1.0
    label: Optional[str] = None


@dataclass
class State:
    """
    Game state containing flags and variables.
    """
    
    flags: Dict[str, bool] = field(default_factory=dict)
    vars: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Context:
    """
    Immutable context passed to scripts.
    """
    
    api_version: str
    node_id: str
    speaker: str
    target: str
    mood: str
    line_text: str
    exits: List[Exit]
    state: State
    rng_seed: int
    time_budget_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for script consumption.
        """
        pass


@dataclass
class TextPatch:
    """
    Text transformation options.
    """
    
    prepend: str = ""
    append: str = ""
    replace: Optional[str] = None


@dataclass
class ScriptResult:
    """
    Result returned from a script execution.
    """
    
    exit: Optional[str] = None
    weights_adjust: Optional[Dict[str, float]] = None
    state_updates: Optional[Dict[str, Dict[str, Any]]] = None
    text_patch: Optional[TextPatch] = None
    mood_override: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScriptResult:
        """
        Create ScriptResult from dictionary returned by the script.
        """
        pass


@dataclass
class PluginManifest:
    """
    Plugin metadata and configuration.
    """
    
    id: str
    name: str
    version: str
    language: str  # "lua" or "js"
    entry_file: str
    capabilities: List[str] = field(default_factory=list)
    description: str = ""
    
    def validate(self):
        """Validate manifest fields."""
        pass


class ScriptCallbacks(Protocol):
    """
    Protocol for script callback functions.

    Implementations provide zero or more lifecycle hooks invoked by the
    scripting engine while traversing dialogue nodes. Each hook receives a
    class `Context` describing the current situation and may return a
    class `ScriptResult` to influence engine behavior (adjust exit weights,
    mutate state, patch text, override mood) or `None` to make no changes.

    Hooks are optional; if a script does not implement a hook, the engine
    treats it as a no-op.
    """

    def on_enter(self, context: Context) -> Optional[ScriptResult]:
        """
        Called when entering a node.

        :param context: Immutable context for the current node entry.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    def before_dialogue(self, context: Context) -> Optional[ScriptResult]:
        """
        Called before dialogue is displayed to the player.

        Typical uses: last-moment text patches, mood adjustments, or flag
        toggles based on dynamic conditions.

        :param context: Immutable context for the upcoming dialogue.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    def after_dialogue(self, context: Context) -> Optional[ScriptResult]:
        """
        Called after dialogue is displayed.

        Typical uses: recording analytics/flags, unlocking exits, or
        progressing state after the line has been shown.

        :param context: Immutable context for the just-shown dialogue.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    def on_choice(self, context: Context) -> Optional[ScriptResult]:
        """
        Called when presenting or evaluating a choice.

        Typical uses: adjusting exit weights/availability or mutating state
        right before selection processing.

        :param context: Immutable context for the current choice moment.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    def on_leave(self, context: Context) -> Optional[ScriptResult]:
        """
        Called when leaving a node.

        Typical uses: cleanup, bookkeeping, or preparing flags for the next
        node.

        :param context: Immutable context at node exit time.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass


class DefaultScriptCallbacks:
    """
    Reference implementation of class `ScriptCallbacks` with safe defaults.

    This implementation demonstrates how hooks can influence the engine:
      - Apply text patches and mood override before dialogue based on
        conventional keys under `context.state.vars`.
      - Update simple counters after a line is shown.
      - Adjust exit weights during choice evaluation when a mapping is present.

    All hooks are tolerant: if no applicable data is present, they return `None` (no changes).
    """

    @staticmethod
    def on_enter(_: Context):
        """
        No-op on node entry.
        """
        pass

    @staticmethod
    def before_dialogue(context: Context) -> Optional[ScriptResult]:
        """
        Optionally patch text or override mood before dialogue.

        Recognized keys in `context.state.vars` (all optional):
          - `text_prepend` (str): Prefix text to prepend.
          - `text_append` (str): Suffix text to append.
          - `text_replace` (str): Full replacement text (takes precedence).
          - `mood_override` (str): Override the current mood label.

        :param context: Context containing state/vars for this moment.
        :type context: Context
        :returns: A ScriptResult with requested patches/override, or None.
        :rtype: Optional[ScriptResult]
        """
        pass

    @staticmethod
    def after_dialogue(context: Context) -> Optional[ScriptResult]:
        """
        Increment a simple counter after dialogue is displayed.

        Updates `state.vars.lines_shown` as an example of state mutation.
        If the counter does not exist, it is initialized to 1.

        :param context: Context for the just-shown dialogue.
        :type context: Context
        :returns: ScriptResult with state update, or None on error.
        :rtype: Optional[ScriptResult]
        """
        pass

    @staticmethod
    def on_choice(context: Context) -> Optional[ScriptResult]:
        """
        Adjust exit weights when a mapping is present.

        Recognized key in `context.state.vars`:
          - `weights_adjust` (dict[str, float]): Per-exit weight adjustments.

        :param context: Context for the current choice moment.
        :type context: Context
        :returns: ScriptResult carrying weights_adjust, or None if absent/invalid.
        :rtype: Optional[ScriptResult]
        """
        pass

    @staticmethod
    def on_leave(_: Context):
        """
        No-op on node exit.
        """
        pass
