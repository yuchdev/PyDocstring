"""Tests for SmartEnvelopeSegmenter using synthetic envelopes.

The goal is to exercise merging/removal logic around the animation-level
thresholds:

anim_min_silence_ms = 300
anim_min_speech_ms  = 400

We validate both the total duration and the resulting segments.
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

import pytest

# Adjust import paths to your project layout as needed.
# Here we assume SmartEnvelopeSegmenter and Envelope live in
# `pipelines.voice.io.audio`.
from pipelines.voice.audio.envelope import Envelope
from pipelines.voice.audio.envelope_segmenter import SmartEnvelopeSegmenter


# Sample envelopes and expected segments for SmartEnvelopeSegmenter tests.
# Each sample uses a fixed envelope sampling rate of 50 frames per second
# (interval_ms = 20), so N samples represent N * 20 milliseconds.
@dataclass
class EnvelopeSample:
    """Single test case for SmartEnvelopeSegmenter.

    Attributes:
        name:
            Human-readable identifier for the sample, used as pytest ID.
        interval_ms:
            Envelope sampling interval in milliseconds.
        samples:
            List of normalized RMS values in [0.0, 1.0].
        anim_min_silence_ms:
            Minimal internal pause duration to keep as the separate segment.
        anim_min_speech_ms:
            Minimal internal speech duration to keep as the separate segment.
        expected_duration_ms:
            Expected total duration in milliseconds (len(samples) * interval_ms).
        expected_segments:
            Expected list of segments in the JSON-friendly form:

            [{"start": int, "activity": "speech" | "pause"}, ...]
    """
    pass


def _duration(num_frames: int, interval_ms: int) -> int:
    """Compute duration in milliseconds for a given number of envelope frames.

    Args:
        num_frames: Number of frames in the envelope.
        interval_ms: Milliseconds per frame (sampling interval).

    Returns:
        Total duration in milliseconds.
    """
    pass


# Common defaults used across most tests
DEFAULT_INTERVAL = 20  # 50 frames per second
DEFAULT_SILENCE_MIN = 300
DEFAULT_SPEECH_MIN = 400


# ------------------------------------------------------------------
# Sample envelopes
# ------------------------------------------------------------------

# 1) Pure silence, 1 second (should be a single pause segment)
pure_silence_samples = [0.0] * 50  # 50 * 20ms = 1000ms

# 2) Pure speech, 1 second (single speech segment)
pure_speech_samples = [0.8] * 50

# 3) Pause (300ms) -> Speech (1200ms) -> Pause (500ms)
#    All segments at or above thresholds: should keep all three.
#    15 frames pause (15*20=300), 60 frames speech (1200), 25 frames pause (500)
psp_samples = (
    [0.01] * 15 +      # pause ~300ms
    [0.9] * 60 +       # speech ~1200ms
    [0.02] * 25        # pause ~500ms
)  # total 100 frames => 2000ms

# 4) Speech (500ms) -> short Pause (200ms) -> Speech (500ms)
#    Pause < anim_min_silence_ms => merged into speech => single speech segment.
sps_short_pause_samples = (
    [0.7] * 25 +       # speech ~500ms
    [0.02] * 10 +      # pause ~200ms (to be removed)
    [0.75] * 25        # speech ~500ms
)  # total 60 frames => 1200ms

# 5) Pause (500ms) -> short Speech (200ms) -> Pause (500ms)
#    Speech < anim_min_speech_ms => absorbed into pause => single pause.
ps_short_speech_p_samples = (
    [0.01] * 25 +      # pause ~500ms
    [0.7] * 10 +       # speech ~200ms (to be removed)
    [0.02] * 25        # pause ~500ms
)  # total 60 frames => 1200ms

# 6) Chain: speech (300ms) -> pause (400ms) -> speech (300ms)
#    Speech segments below 400ms and pause >= 300ms.
#    After final enforcement, both short speech islands are merged away,
#    resulting effectively in a single pause segment.
chain_sps_short_speech_samples = (
    [0.8] * 15 +       # speech ~300ms (short)
    [0.02] * 20 +      # pause  ~400ms
    [0.85] * 15        # speech ~300ms (short)
)  # total 50 frames => 1000ms

# 7) Borderline: speech (400ms) -> pause (300ms) -> speech (400ms)
#    Exactly at thresholds, so all three segments should be kept.
borderline_sps_samples = (
    [0.8] * 20 +       # speech 400ms
    [0.02] * 15 +      # pause  300ms
    [0.85] * 20        # speech 400ms
)  # total 55 frames => 1100ms

# 8) Entire utterance shorter than anim_min_speech_ms: ~300ms of speech only
#    Should remain a single speech segment despite being below 400ms.
short_utterance_speech_samples = [0.8] * 15  # 15 * 20 = 300ms


SAMPLE_ENVELOPES: List[EnvelopeSample] = [
    EnvelopeSample(
        name="pure_silence",
        interval_ms=DEFAULT_INTERVAL,
        samples=pure_silence_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(pure_silence_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0, "activity": "pause"},
        ],
    ),
    EnvelopeSample(
        name="pure_speech",
        interval_ms=DEFAULT_INTERVAL,
        samples=pure_speech_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(pure_speech_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0, "activity": "speech"},
        ],
    ),
    EnvelopeSample(
        name="pause-speech-pause_all_above_thresholds",
        interval_ms=DEFAULT_INTERVAL,
        samples=psp_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(psp_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0,    "activity": "pause"},   # 0..300ms
            {"start": 300,  "activity": "speech"},  # 300..1500ms
            {"start": 1500, "activity": "pause"},   # 1500..2000ms
        ],
    ),
    EnvelopeSample(
        name="speech-pause-speech_short_pause_merged",
        interval_ms=DEFAULT_INTERVAL,
        samples=sps_short_pause_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(sps_short_pause_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0, "activity": "speech"},  # 0..1200ms, single block
        ],
    ),
    EnvelopeSample(
        name="pause-speech-pause_short_speech_removed",
        interval_ms=DEFAULT_INTERVAL,
        samples=ps_short_speech_p_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(ps_short_speech_p_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0, "activity": "pause"},  # 0..1200ms, single block
        ],
    ),
    EnvelopeSample(
        name="chain_speech-pause-speech_short_speech_merged_to_pause",
        interval_ms=DEFAULT_INTERVAL,
        samples=chain_sps_short_speech_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(chain_sps_short_speech_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0, "activity": "pause"},  # short speech islands removed
        ],
    ),
    EnvelopeSample(
        name="borderline_speech-pause-speech_kept",
        interval_ms=DEFAULT_INTERVAL,
        samples=borderline_sps_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(borderline_sps_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0,   "activity": "speech"},  # 0..400ms
            {"start": 400, "activity": "pause"},   # 400..700ms
            {"start": 700, "activity": "speech"},  # 700..1100ms
        ],
    ),
    EnvelopeSample(
        name="short_single_speech_utterance_kept",
        interval_ms=DEFAULT_INTERVAL,
        samples=short_utterance_speech_samples,
        anim_min_silence_ms=DEFAULT_SILENCE_MIN,
        anim_min_speech_ms=DEFAULT_SPEECH_MIN,
        expected_duration_ms=_duration(len(short_utterance_speech_samples), DEFAULT_INTERVAL),
        expected_segments=[
            {"start": 0, "activity": "speech"},  # single short segment
        ],
    ),
]


@pytest.mark.parametrize("sample", SAMPLE_ENVELOPES, ids=lambda s: s.name)
def test_smart_segmenter_samples(sample: EnvelopeSample):
    """[Unit] SmartEnvelopeSegmenter: produces expected segments for synthetic envelopes

    Scenario:
        Construct an `Envelope` from predefined sample data and run
        `SmartEnvelopeSegmenter.compute_segments` with configured thresholds.

    Boundaries:
        - Handles all-pause and all-speech envelopes.
        - Merges short pauses/speech islands below animation thresholds.
        - Keeps segments exactly at threshold lengths.

    On failure, first check:
        - The sample's `interval_ms` and `expected_duration_ms` alignment.
        - Thresholds passed to the segmenter.
        - The JSON conversion of produced segments.
    """
    pass
