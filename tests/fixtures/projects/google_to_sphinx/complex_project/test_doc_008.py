from __future__ import annotations

from typing import Protocol, Tuple, List, Optional

from pipelines.voice.audio.envelope import Envelope, Segment
from pipelines.voice.utils.log_helper import logger


class IEnvelopeSegmenter(Protocol):
    """Protocol for components that derive speech/pause segments from envelopes.

    Implementations transform an :class:`Envelope` (RMS values + interval)
    into a debounced sequence of speech/pause segments suitable for driving
    animation timelines.
    """
    pass


class SmartEnvelopeSegmenter(IEnvelopeSegmenter):
    """Heuristic segmenter turning RMS envelopes into speech/pause segments.

    This class is intentionally independent of low-level audio decoding.
    It consumes :class:`Envelope` instances and produces:

    * Total duration in milliseconds.
    * An ordered list of :class:`Segment` change-points suitable for driving
    mouth / face animation.

    Classification strategy:

    1. Each envelope frame is classified as `"speech"` or `"pause"`
    by a simple amplitude threshold.
    2. Consecutive frames of the same class are grouped into "runs".
    3. Two debouncing / smoothing rules are applied at the run level:

    * **Short internal pauses** are merged into speech:

    Any `"pause"` run shorter than `anim_min_silence_ms` that is
    *between* two `"speech"` runs is merged into the neighbors,
    so tiny breath-holds do not split the animation.

    * **Tiny isolated speech islands** are removed:

    Any `"speech"` run shorter than `anim_min_speech_ms` that is
    *between* two `"pause"` runs is treated as noise and merged
    into surrounding pause.

    4. Runs are converted into time-domain segments.
    5. A final pass enforces minimal segment durations:

    * For each segment, its duration is compared against

    - `anim_min_silence_ms` if it is a pause.
    - `anim_min_speech_ms` if it is speech.

    * Short segments are merged into their neighbors until all segments
    meet their minimal durations, or only a single segment remains.

    This makes the thresholds behave as *hard minimums* for internal
    segments while still allowing short one-segment clips (e.g. a 250 ms
    standalone “Yes”) to remain intact.
    """
    pass


class NullEnvelopeSegmenter(IEnvelopeSegmenter):
    """Null envelope implementation that always returns zero duration."""
    pass
