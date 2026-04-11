"""Voice training service: discovery, embedding, and NPZ serialization.

This module encapsulates the higher-level logic for building a per-character
voice cache from training WAV files. It intentionally keeps the low-level
audio primitives (loading, embedding, ASR) in :mod:`audio` and uses the
filesystem abstraction from :mod:`filesystem`.

The goal is to keep :mod:`audio` free of training responsibilities while
allowing operations to orchestrate via a single service call.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Protocol, BinaryIO, cast

import numpy as np

from pipelines.voice.audio.audio_processor import IAudioProcessor
from pipelines.voice.io.filesystem import IFileSystem
from pipelines.voice.utils.log_helper import logger


class IVoiceTrainingService(Protocol):
    """Protocol for voice training operations.

    Responsibilities:
    - Discover per-character training sets from a root directory.
    - Build a voice cache by computing speaker embeddings and centroids.
    - Serialize the cache to NPZ bytes, compatible with the legacy pipeline.
    """

    def discover_training_sets(self, root: Path) -> dict[str, list[Path]]:
        """Discover WAV files grouped by character.

        Supports two layouts under `root`:
          1) root/CharacterName/*.wav
          2) root/NN-CharacterName.wav (flat layout)

        :param root: Root directory to scan.
        :type root: pathlib.Path
        :returns: Mapping of character -> sorted list of WAV paths.
        :rtype: dict[str, list[pathlib.Path]]
        """
        pass

    def build_voice_cache(self, train_sets: dict[str, list[Path]]) -> tuple[dict[str, np.ndarray], dict[str, list[str]]]:
        """Compute voice centroids and meta from training sets.

        :param train_sets: Mapping character -> list of WAV file paths.
        :type train_sets: dict[str, list[pathlib.Path]]
        :returns: Tuple of (centroids_by_char, meta_files_by_char)
                  where centroids are shaped (1, D) and meta lists contain file paths.
        :rtype: tuple[dict[str, np.ndarray], dict[str, list[str]]]
        """
        pass

    def serialize_cache(self, centroids: dict[str, np.ndarray], meta: dict[str, list[str]]) -> bytes:
        """Serialize centroids + meta into NPZ bytes.

        The NPZ format is kept backward compatible with the legacy pipeline:
        - Each centroid stored under the key `centroid__{character}`.
        - `meta` key stores a numpy object array of the dict mapping
          character -> list of file path strings.

        :param centroids: Per-character centroid matrices (1, D)
        :param meta: Per-character lists of training file path strings
        :returns: Bytes of a .npz file created via `numpy.savez`
        :rtype: bytes
        """
        pass


@dataclass
class VoiceTrainingService(IVoiceTrainingService):
    """Concrete implementation of :class:`IVoiceTrainingService`.

    :param fs: Filesystem abstraction.
    :type fs: IFileSystem
    :param audio: Audio processing backend providing load + embedding.
    :type audio: IAudioProcessor
    """

    fs: IFileSystem
    audio: IAudioProcessor

    def discover_training_sets(self, root: Path) -> dict[str, list[Path]]:
        """Discover per-character training WAV sets under `root`.

        The function supports two layouts:

        1. Subdirectories: `root/CharacterName/*.wav`.
        2. Flat files: `root/NN-CharacterName.wav` (index prefix optional).

        :param root: Root directory to scan for training audio.
        :type root: pathlib.Path
        :returns: Mapping of character name to a sorted list of WAV paths.
        :rtype: dict[str, list[pathlib.Path]]
        """
        pass

    def build_voice_cache(self, train_sets: dict[str, list[Path]]) -> tuple[dict[str, np.ndarray], dict[str, list[str]]]:
        """Compute per-character embedding centroids and meta information.

        For each character, this function loads each WAV file, computes a
        speaker embedding via :meth:`IAudioProcessing.embed_speaker`, and then
        averages embeddings to produce a centroid shaped `(1, D)`.

        :param train_sets: Mapping of character to the list of WAV file paths.
        :type train_sets: dict[str, list[pathlib.Path]]
        :returns: Tuple `(centroids_by_char, meta_files_by_char)` where
                  centroids are numpy arrays shaped `(1, D)` and meta lists
                  contain training file paths.
        :rtype: tuple[dict[str, numpy.ndarray], dict[str, list[str]]]
        """
        pass

    def serialize_cache(self, centroids: dict[str, np.ndarray], meta: dict[str, list[str]]) -> bytes:
        """Serialize centroids and meta into an NPZ byte stream.

        The NPZ contains keys `centroid__{character}` for each centroid and a
        `meta` key which stores a numpy object array of the mapping
        `character -> list[str]`.

        :param centroids: Mapping of character to centroid arrays shaped `(1, D)`.
        :type centroids: dict[str, numpy.ndarray]
        :param meta: Mapping of character to lists of training file paths (as str).
        :type meta: dict[str, list[str]]
        :returns: Bytes of the generated `.npz` archive.
        :rtype: bytes
        """
        pass
