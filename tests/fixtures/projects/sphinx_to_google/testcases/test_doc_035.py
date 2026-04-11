"""Config validation for voice pipeline commands.

All CLI arguments are first parsed into small dataclasses (one per command),
then validated here. Filesystem-related checks are delegated to
:class:`FsValidator` so that all path semantics stay in one place.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pipelines.voice.utils.log_helper import logger
from pipelines.voice.io.filesystem import IFileSystem


class ConfigError(RuntimeError):
    """Raised when CLI configuration is invalid."""
    pass


# --------------------------------------------------------------------------- #
# Configuration dataclasses                                                   #
# --------------------------------------------------------------------------- #
@dataclass
class ModelSetupConfig:
    """Configuration for the `model-setup` command."""

    model_dir: Path
    model_name: str
    dry_run: bool
    force: bool


@dataclass
class TrainVoicesConfig:
    """Configuration for the `train-voices` command."""

    train_dir: Path
    cache_dir: Path
    sample_rate: int
    dry_run: bool
    force: bool


@dataclass
class AlignPreSlicedConfig:
    """Configuration for the `align-pre-sliced` command."""

    script_in: Path
    voiceover_root: Path
    warnings_to_exit: Optional[int]
    threshold: float
    dry_run: bool = False
    force: bool = False
    cache_dir: Optional[Path] = None
    model_dir: Optional[Path] = None


@dataclass
class AppendJsonVoiceoverConfig:
    """Configuration for the `append-json-voiceover` command."""

    script_in: Path
    script_out: Optional[Path]
    voiceover_root: Path
    envelope_root: Optional[Path]
    warnings_to_exit: Optional[int]
    interval_ms: int
    anim_min_silence_ms: int
    anim_min_speech_ms: int
    dry_run: bool
    force: bool


@dataclass
class AlignWithContentConfig:
    """Configuration for the `align-with-content` command.

    This command aligns voiceover metadata from a modified play script back into
    the game content JSON nodes. It supports in-place updates as well as writing
    into a separate output content root.

    Attributes
    ----------
    script_in:
        Path to modified play content: either a single `day-NN.json` file or
        a directory containing multiple `day-*.json` files.
    content_root_in:
        Root of the game content tree (Days/..), used as the read-only source.
    content_root_out:
        Optional output root for the updated game content. When `None`,
        defaults to `content_root_in` (in-place update).
    warnings_to_exit:
        Optional limit of consecutive non-matching dialogue warnings that should
        trigger a non-zero exit.
    dry_run:
        When True, do not write or copy anything; only log planned actions.
    force:
        When True, allow overwriting an existing `content_root_out`.
    active_content_root:
        Effective root where updates will be written (resolved by the CLI
        runner before executing the operation). When `None`, the operation
        will treat `content_root_in` as both read and write root (legacy
        behaviour).
    """

    script_in: Path
    content_root_in: Path
    content_root_out: Optional[Path]
    warnings_to_exit: Optional[int]
    dry_run: bool
    force: bool
    active_content_root: Optional[Path] = None


@dataclass
class RemoveVoiceoverConfig:
    """Configuration for the `remove-voiceover` command."""

    script_in: Path
    script_out: Path
    warnings_to_exit: Optional[int]
    dry_run: bool
    force: bool


# --------------------------------------------------------------------------- #
# Validators                                                        #
# --------------------------------------------------------------------------- #
class FsValidator:
    """Declarative filesystem validator.

    All filesystem-related checks live here. Each method either:

    * raises :class:`ConfigError` (default), or
    * logs an error and returns `False` when `raise_exception=False`.

    Callers handle optional paths (they only call these methods when
    a value is not `None`).
    """

    def __init__(self, fs: IFileSystem, *, raise_exception: bool = True):
        """Create a filesystem validator.

        :param fs: Filesystem abstraction to operate on.
        :type fs: IFileSystem
        :param raise_exception: When True, methods raise ConfigError on failure;
            when False, they log errors and return `False` instead.
        :type raise_exception: bool
        """
        pass

    def _fail(self, message: str) -> bool:
        """Either raise ConfigError or log and return False based on policy."""
        pass

    def ensure_exists(self, path: Path, desc: str) -> bool:
        """Ensure the path exists (file or directory)."""
        pass

    def ensure_not_exists(self, path: Path, desc: str) -> bool:
        """Ensure the path does *not* exist."""
        pass

    def ensure_dir(self, path: Path, desc: str, *, must_exist: bool = True) -> bool:
        """Ensure the path is a directory (optionally must already exist)."""
        pass

    def ensure_file(self, path: Path, desc: str, *, must_exist: bool = True) -> bool:
        """Ensure the path is a file (optionally must already exist)."""
        pass

    def ensure_empty_dir(self, path: Path, desc: str, *, allow_missing: bool = True) -> bool:
        """Ensure directory is empty (or missing if allow_missing=True)."""
        pass

    def ensure_empty_or_overwritable(self, path: Path, desc: str, *, force: bool) -> bool:
        """Model-setup semantics for target directory.

        - If directory does not exist → OK.
        - If directory exists and is empty → OK.
        - If directory exists and is non-empty:
            - if force is False → error
            - if force is True → OK (caller is allowed to remove it).
        """
        pass

    def ensure_overwritable_file(self, path: Path, desc: str, *, force: bool) -> bool:
        """Ensure a file path is safe to write.

        OK if the path does not exist. If it exists:
        - with force=False → error
        - with force=True  → allowed (caller may overwrite).
        """
        pass


class VoicePipelineValidator:
    """Validate configuration objects before running operations.

    One method per command, delegating all filesystem checks to
    :class:`FsValidator`.
    """

    def __init__(self, fs: IFileSystem):
        """Initialize validator with a concrete filesystem implementation.

        :param fs: Filesystem used to check paths for existence and types.
        :type fs: IFileSystem
        """
        pass

    def validate_model_setup(self, cfg: ModelSetupConfig):
        """Validate config for `model-setup` command."""
        pass

    def validate_train_voices(self, cfg: TrainVoicesConfig):
        """Validate config for `train-voices` command.

        Resolve the effective NPZ output path from `cache_dir`, which may be either
        a directory or a file path. Keep logic compatible with action resolver:
        - if cache_dir is an existing directory → cache_dir/voices.npz
        - if cache_dir endswith .npz → use as-is
        - otherwise → append .npz extension
        """
        pass

    def validate_align_pre_sliced(self, cfg: AlignPreSlicedConfig):
        """Validate config for `align-pre-sliced`."""
        pass

    def validate_append_json(self, cfg: AppendJsonVoiceoverConfig):
        """Validate config for `append-json-voiceover`."""
        pass

    def validate_align_with_content(self, cfg: AlignWithContentConfig):
        """Validate config for `align-with-content`."""
        pass

    def validate_remove_voiceover(self, cfg: RemoveVoiceoverConfig):
        """Validate config for `remove-voiceover`."""
        pass
