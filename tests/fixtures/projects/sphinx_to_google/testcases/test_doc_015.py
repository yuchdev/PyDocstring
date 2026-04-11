"""GameWindow implements the main GUI: avatar, chat log, group dynamics, and controls.

Why:
- Acts as a mediator between the engine layer (EventGraph/EventProgression) and Qt widgets.
- Encapsulates UI state transitions (choices, day navigation, voiceover visuals).

Workflow:
- Engine emits events via Game.advance_event; GameWindow renders them and drives choices.
- For dialogue with voiceover, it extracts an amplitude envelope and starts VoiceoverWidget
  in tandem with audio playback so visuals are aligned.

Context:
This module is imported by the desktop app entry point and heavily used by tests to verify
assets, paths, and startup sequences.
"""

from __future__ import annotations

import sys
import os
import re
from functools import partial
from pathlib import Path
from typing import Callable, Optional
from collections import OrderedDict


from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QProgressBar, QLabel, QPushButton,
    QHeaderView, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap

# Support running this file directly: ensure project root on sys.path
if __package__ in (None, ""):
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from labyrinth.domain.settings import Settings
from labyrinth.domain.assets import AssetLocator
from labyrinth.clients.progress import ProgressRecorder, ProgressReplayer

from game.errors import ValidationError
from game.game import Game
from game.event_progression import EventProgression
from game.log_helper import logger
from game.sound import play_voiceover, play_effect, extract_envelope
from game.voiceover_widget import VoiceoverWidget


def rewrite_qss_urls(qss_text: str, resource_resolver: Callable[[str], str]) -> str:
    """Rewrite url() references in QSS stylesheets to resolved absolute paths.

    Processes Qt stylesheet text to replace relative url() references with
    absolute paths resolved via the resource_resolver callback. Handles
    special cases like legacy 'resources/background' paths.

    Args:
        qss_text: The QSS stylesheet text to process
        resource_resolver: Callback function to resolve resource paths

    Returns:
        The QSS text with rewritten url() references
    """
    pass


def project_root() -> Path:
    """Return absolute path to the project root (one level above this package)."""
    pass


def resource_path(*parts: str) -> str:
    """Build an absolute path from project root and provided parts."""
    pass


def emotion_label(emotion: str) -> str:
    """Return a simple display label for an emotion string.

    Fallback behavior: capitalize the input; if None or empty, return an empty string.
    """
    pass


class GameWindow(QMainWindow):
    """
    Main GUI window for the game.
    """

    # Interval between reading of voiceover envelope
    DEFAULT_INTERVAL_MS = 20

    # Default number of bars on VoiceoverWidget
    DEFAULT_BAR_COUNT = 70

    def __init__(self, game: Game, progression: EventProgression):
        """Initialize the main game window with UI components and game state.

        Sets up the GUI layout, loads game entities (characters, events, emotions),
        initializes the event progression system, and attempts to restore from
        saved progress if available. If no progress exists, starts a fresh day.

        Workflow:
        1. Initialize game instance (provided or default)
        2. Set up progression controller for event state
        3. Create UI widgets and layout
        4. Attempt to restore from saved progress
        5. If no progress, load the current day from scratch

        Args:
            game: Optional Game instance to use; creates default if None
            progression: Optional EventProgression instance; creates default if None

        Raises:
            ValidationError: If progress.directory setting is missing
        """
        pass

    def init_ui(self):
        """Initialize the user interface."""
        pass

    def replay_progress_sequence(self, sequence):
        """Render a previously computed progress sequence using the Game logic.

        Delegates sequence materialization to Game and only handles display here.
        """
        pass

    @staticmethod
    def clear_layout(layout: QVBoxLayout):
        """Remove all widgets from a QVBoxLayout.

        Iterates through the layout and deletes all widgets to prepare for
        rebuilding or cleanup.

        Args:
            layout: The QVBoxLayout to clear
        """
        pass

    @staticmethod
    def create_grid_layout(layout: QGridLayout, rows: int, cols: int, widgets):
        """Populate a QGridLayout with a rectangular matrix of widgets.

        Why: convenience for consistent grid assembly across panels.
        :param layout: target QGridLayout to populate
        :param rows: expected number of rows
        :param cols: expected number of columns
        :param widgets: list[list[QWidget|None]] sized rows x cols; None values are skipped
        """
        pass

    def show_choices(self, raw_options: dict):
        """Render interactive choice panel (A/B/C) using exit options payload."""
        pass  # disable Next/Prev while waiting for a choice

    def hide_choices(self):
        """Hide choice panel and reset internal mappings/state; re-enable navigation buttons."""
        pass

    def on_engine_signal(self, event_name: str, payload: Optional[dict] = None):
        """Dispatcher for engine -> GUI signals (currently only 'choice_required')."""
        pass

    def on_choice_selected(self, letter: str):
        """Resolve clicked a choice letter to a full key and continue progression."""
        pass

    def resolve_and_load_next_from_exit(self, exit_obj: dict) -> bool:
        """Resolve a 'next' exit and autoload the next node; return True if progressed."""
        pass

    def is_interactive_exit(self, event) -> bool:
        """Heuristics to detect interactive exits by type or presence of options."""
        pass

    @staticmethod
    def extract_exit_options(event) -> Optional[dict]:
        """Return options mapping from event or its payload when present."""
        pass

    @staticmethod
    def normalize_display_options(raw) -> OrderedDict:
        """Collapse A1/A2 keys to single A with first prompt, returning OrderedDict.

        Normalizes choice options from various formats (list or dict) into a
        consistent OrderedDict structure. Handles stripping numeric suffixes
        from keys (e.g., 'A1' becomes 'A') and prioritizes the first prompt
        when multiple variants exist.

        Args:
            raw: Raw options data (list of dicts or dict)

        Returns:
            OrderedDict mapping normalized keys to prompt strings
        """
        pass

    def apply_background_styling(self):
        """Load external QSS, rewrite asset URLs to absolute, and apply to the app."""
        pass

    def preload_avatar_images(self):
        """Preload and cache scaled avatar pixmaps to avoid repeated disk loads/leaks."""
        pass

    def create_character_list(self):
        """Assemble the left-side character list with live stats columns."""
        pass

    def create_chat_events(self):
        """Assemble the chat/events text panel with monospaced font and auto-scroll."""
        pass

    def create_group_dynamics(self):
        """Assemble the mid-left group dynamics panel (mood/tension/trust)."""
        pass

    def create_avatar_voice(self):
        """Assemble the avatar panel and attach the VoiceoverWidget under the stats_grid."""
        pass

    def load_labyrinth_avatar(self):
        """Ensure the default environment avatar (Labyrinth) is displayed and cached."""
        pass

    def update_character_avatar(self, character_name):
        """Swap the avatar to the current speaker, updating the stats_labels too."""
        pass

    def create_choice_panel(self):
        """Create an initially hidden panel to render branch choices at node exits."""
        pass

    def create_controls(self):
        """Create navigation controls (next/prev step and day switches)."""
        pass

    def load_current_day(self):
        """Reset choice panel, show default avatar, and load events for current day."""
        pass

    def next_step(self):
        """Advance engine by one event, render it, and handle exits/voiceover visuals."""
        pass

    def prev_step(self):
        """Undo the last event by reloading day and replaying up to prior index."""
        pass

    def next_day(self):
        """Increment current_day and load the new day's events."""
        pass

    def prev_day(self):
        """Decrement current_day when possible and reload the day."""
        pass

    def reload_day_to_index(self):
        """Replay events up to current_event_index to rebuild UI state after undo."""
        pass

    def _current_ctx_vars(self) -> dict:
        """Build a JS processing context snapshot (group/characters/emotions maps)."""
        pass

    def _process_event_dict(self, event: dict):
        """Run JS semantics for a dict-shaped event and apply resulting effects."""
        pass

    def _persist_group_snapshot(self):
        """Persist current roster/stats into mock progress JSON (no-op in non-mock)."""
        pass

    def _restore_group_from_history(self, history: Optional[dict]):
        """Upsert characters and restore active order/control routing from history dict.

        Restores the character group state from a saved history snapshot, including
        character stats, active roster order, and control routing (AI/user/return).
        This ensures that saved game state is fully rehydrated on startup.

        Args:
            history: Dictionary containing saved progress with group snapshot

        Raises:
            ValidationError: If schema_version is invalid or missing
        """
        pass

    def load_avatar_image(self, avatar_key: str) -> Optional[QPixmap]:
        """Return a cached pixmap by exact avatar key (PNG stem)."""
        pass

    def _avatar_cache_key_for_name(self, avatar_key: str) -> Optional[str]:
        """Return the cache key if present (no resolution)."""
        pass

    def display_event(self, event):
        """Append a formatted message to the chat based on event type and payload."""
        pass

    def show_speaking_animation(self, character, event_type=None):
        """Legacy helper to briefly show speaking animation for non-VO paths."""
        pass

    def enforce_avatar_policy_after_event(self, event):
        """Ensure avatar matches policy after events like LEAVE/EXIT or day transitions."""
        pass

    def update_display(self):
        """Refresh all panels (characters, dynamics, controls, stats)."""
        pass

    def update_character_list(self):
        """Populate the character table with the current active roster and stats."""
        pass

    def update_group_dynamics(self):
        """Update mood emoji/label and tension bar from current group snapshot."""
        pass

    def update_controls(self):
        """Enable/disable navigation depending on choice state and event indices."""
        pass

    def update_character_stats(self):
        """Update the right-side stats labels to reflect current_character selection."""
        pass

    @staticmethod
    def _voiceover_base_dir() -> Optional[Path]:
        """Return base directory for voiceover files as configured in settings."""
        pass

    def _resolve_voiceover_path(self, event: dict) -> Optional[Path]:
        """Compute the voiceover file path for the event within the day-subfolder.

        Supports both legacy string voiceover fields and new dict format
        {'filename': str, 'envelope': [...]}.
        """
        pass

    def _play_voiceover_for_event(self, event: dict) -> bool:
        """Play voiceover audio for an event and animate envelope.

        Returns True if playback started. Supports legacy string voiceover or new dict
        format {'filename': str, 'envelope': str, 'interval_ms': int}.
        """
        pass
