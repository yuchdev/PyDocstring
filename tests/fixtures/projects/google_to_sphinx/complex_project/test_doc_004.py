from __future__ import annotations

import io
import json

from pathlib import Path
from typing import Tuple, List, Optional

import numpy as np
import soundfile as sf
from vosk import Model, KaldiRecognizer

from pipelines.voice.utils.log_helper import logger


class IAudioProcessor:
    """Abstract audio processing backend.

    The voice pipeline depends only on this interface. Concrete implementations
    (e.g. :class:`ResemblyzerVoskAudioProcessing`) are injected into higher-level
    components such as :class:`AudioFile` or operation classes.

    All methods raise :class:`NotImplementedError` in this base class.
    """
    pass


class ResemblyzerVoskAudioProcessor(IAudioProcessor):
    """Concrete audio backend using soundfile, resemblyzer and Vosk.

    This implementation is intended for production use. It owns:

    * A long-lived :class:`resemblyzer.VoiceEncoder` instance for speaker
    embeddings.
    * An optional long-lived :class:`vosk.Model` instance for ASR.

    Other parts of the pipeline (e.g. :class:`AudioFile`) depend only on the
    """
    pass


class NullAudioProcessing(ResemblyzerVoskAudioProcessor):
    """Audio processing backend for dry-run mode.

    This subclass disables speaker embedding and ASR by overriding the
    respective methods to always return `None`.
    """
    pass
