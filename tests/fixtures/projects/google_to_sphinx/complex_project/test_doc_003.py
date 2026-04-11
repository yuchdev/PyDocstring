"""AudioFile entity: rich wrapper around a single audio path.

The :class:`AudioFile` class is a small, focused domain object that binds:

* A concrete file path.
* An :class:`IAudioProcessing` backend.

It provides lazy access to decoded samples and caches expensive derived values:

* Duration in milliseconds.
* RMS envelope for arbitrary intervals.
* Speaker embedding.
* ASR transcript.

This keeps higher-level operations (e.g. `align-pre-sliced`,
`append-json-voiceover`) simple: they ask the :class:`AudioFile` for what
they need, without worrying about how decoding/ASR/embedding are implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from pipelines.voice.audio.audio_processor import IAudioProcessor


@dataclass
class AudioFile:
    """Rich audio entity bound to a single file path.

    Attributes:
            path: Path to the underlying audio file.
            processor: Audio backend implementing :class:`IAudioProcessing`.

        Cached state:

        * `_samples` / `_sr` - decoded mono waveform and sample rate.
        * `_envelopes` - mapping `interval_ms -> [float]`.
        * `_embedding` - speaker embedding vector (numpy array).
        * `_text` - ASR transcript (str).
        * `_duration_ms` - integer duration in milliseconds.
    """
    pass
