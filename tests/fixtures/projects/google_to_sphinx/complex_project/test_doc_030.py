from __future__ import annotations

import random
from typing import Optional, Sequence

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from PySide6.QtWidgets import QWidget


class VoiceoverWidget(QWidget):
    """Animated voiceover indicator showing decorative sound bars driven by a real audio envelope.

    Public API:
    start_voiceover(speaker, envelope_frames: Sequence[float], interval_ms: int)
    stop_voiceover()
    is_active()

    Why:
    Provides a compact, non-intrusive visualization of voiceover playback that
    mirrors perceived loudness, adding clarity and polish to dialogue.

    Workflow:
    - Game computes an RMS envelope from a WAV/OGG file.
    - Widget is started with the envelope and a matching interval.
    - A QTimer advances frames; when frames are exhausted it decays and hides.

    Context:
    Self-contained QWidget used in the right-side avatar panel; it does not
    control audio playback, only mirrors it visually.
    """
    pass
