from __future__ import annotations

import array
import struct

from pathlib import Path
from typing import Protocol

from pipelines.voice.audio.audio_processor import IAudioProcessor
from pipelines.voice.audio.envelope import Envelope
from pipelines.voice.io.filesystem import IFileSystem
from pipelines.voice.utils.log_helper import logger


class IEnvelopeWriter(Protocol):
    """Protocol for components that compute and persist audio envelopes."""
    pass


class RealEnvelopeWriter:
    """Envelope writer that uses :class:`IAudioProcessing` and :class:`IFileSystem`.

    The real project uses a compact binary `.dat` format; this skeleton keeps
    envelopes as JSON for readability. The shape of the API matches what the
    pipeline needs: compute from audio, then write to a sidecar file.
    """
    pass


class NullEnvelopeWriter(RealEnvelopeWriter):
    """Envelope writer that never persists anything.

    Used in dry-run mode: it computes the envelope (if needed) but only
    logs where it *would* write the file.
    """
    pass
