from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from labyrinth.clients.progress import ProgressReplayer
from labyrinth.domain.settings import Settings

from game.errors import ValidationError
from game.game import Game


@dataclass
class ProgressState:
    """Lightweight container for progression-related state.

    This deliberately mirrors the minimal state that used to live on
    `GameWindow` so that the view can delegate all progression details
    here while remaining a pure UI layer.
    """
    pass


class EventProgression:
    """Orchestrates progression of :class:`Game` events.

    This class owns the ephemeral progression state (current events,
    index and replay flags) that previously lived on `GameWindow` and
    exposes a small, Qt-free API which the view can use to drive the
    model forward.

    It purposefully does *not* know about any widgets; sound effects are
    still triggered from the view based on the replay/suppression
    flags. This keeps the change set minimal while still separating the
    responsibilities.
    """
    pass
