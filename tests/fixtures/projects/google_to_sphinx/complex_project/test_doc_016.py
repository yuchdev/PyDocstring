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
    """Container for potential and active characters with JS-owned group dynamics.

    Owns:
    - a registry of Character objects keyed by canonical name,
    - an ordered active roster (`Active`),
    - a case-sensitive alias map (alias -> canonical).

    Python holds only durable data and performs data exchange with the JS engine.
    All gameplay/social logic happens in JS. Python applies only membership/control
    effects (enter/leave/control.*) requested by JS.

    Args:
        emotions: Global Emotions instance (used when constructing Character).
        characters: Optional map name -> stats to seed/merge characters.
    """
    pass
