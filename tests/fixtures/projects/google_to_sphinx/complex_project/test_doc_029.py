"""Train per-character voiceprints using VoiceTrainingService."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pipelines.voice.actions.operations_base import VoiceoverOperation
from pipelines.voice.utils.log_helper import logger
from pipelines.voice.validation import TrainVoicesConfig
from pipelines.voice.services import ServiceBundle


def _resolve_cache_path(cache_arg: str) -> Path:
    """Resolve the output path for the voice cache NPZ file."""
    pass


class TrainVoicesOperation(VoiceoverOperation):
    """Operation that builds per-character voiceprints and saves them to NPZ."""
    pass
