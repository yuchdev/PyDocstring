def extract_envelope(path: str | Path, interval_ms: int = 55) -> list[float]:
    """Load a precomputed RMS envelope from a companion file.

    The envelope file lives under assets.envelope.directory with the same base name
    as the voiceover audio but extension configured in settings (default 'dat').
    This function no longer performs on-the-fly audio analysis; it simply reads
    the binary envelope format:

    Layout (little-endian):
        4 bytes  magic 'ENV1'
        1 byte   version (currently 0x01)
        4 bytes  uint32 sample count N
        4 bytes  float32 nominal interval_ms (for reference)
        N*4      float32 samples (normalized 0..1)

    Args:
        path: Path to the audio file (wav/ogg) whose envelope we want
        interval_ms: Ignored for generation (kept for backward compat); returned value
                     may have been generated with a different interval; we trust file header.

    Returns:
        List of float amplitudes normalized 0..1. Empty list on failure.
    """
    pass


class TestCases:
    """Durable character storage with a dynamic attribute bag and relationship impacts.

    Everything behavioral is in JS; this class only keeps data and ensures that
    a small set of canonical fields mirror into the bag, and vice versa.

    Canonical fields are:
    - name (str)
    - leadership (int 0..100)
    - intelligence (int 0..100)
    - resilience (int 0..100)
    - description (str)
    - friends (list[str])
    - enemies (list[str])

    Additional fields live in `attributes` and are entirely controlled by JS.
    Relationship impacts are stored in `relation_impact` as a mapping
    target-name -> `friendly|neutral|hostile` (values decided by JS).
    """
    pass


class FileLogSink(LogSink):
    """File-based log sink that writes JSON lines to disk.

    This sink ensures parent directories exist and appends log events
    as JSON lines to the appropriate file.
    """
    pass


class ScriptingLogger:
    """Main dispatcher for scripting logs.

    Routes log events from JS scripts to the appropriate sink/file based on
    script name, playthrough ID, and configuration. Never crashes the game
    even if logging fails.
    """
    pass


class NotFoundError(LegendError):
    """Raised when a requested resource (node, graph, etc.) is not found."""
    pass


class InvalidChoiceError(LegendError):
    """Raised when an invalid choice index is provided."""
    pass

class EventGraph:
    """JS-driven event graph/day progression. Python side keeps only I/O helpers + result caching for GUI."""
    pass

class Game:
    """Core game state container managing emotions, characters, events, and event graph.

    The Game class orchestrates all primary game systems including emotional
    states, character group dynamics, event metadata, and the event flow graph.
    It supports optional JavaScript-driven logic for both event progression
    and character dynamics.
    """
    pass


@dataclass
class AdvanceEventResult:
    """Result container for event progression state.

    Encapsulates all relevant information returned when advancing through
    the event sequence, including the event itself, speaker information,
    voiceover path resolution, and exit transitions.

    Attributes:
        event: The event dictionary, or None if no more events
        show_speaking: Whether to display speaking indicator
        speaker: Character identifier for the speaking character
        voiceover_path: Resolved Path to voiceover audio file
        voiceover_interval_ms: Interval in milliseconds for envelope sampling
        exit: Exit object describing the next transition, if applicable
    """
    pass


class NodeFlow:
    """Bridge to JS node exit resolution.

    This class loads `node_flow.js` and exposes two typed helpers that return a
    normalized Python dict with the canonical triplet: `next_node_id`,
    `next_cluster_id`, and `end`.
    """
    pass


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


@dataclass(frozen=True)
class CharacterFilter:
    """Filter options for :func:`get_characters`.

    Attributes
    ----------
    ids:
    Optional list of character identifiers to restrict the result to.

    search:
    Optional case-insensitive substring to match against character
    `display_name` and `description`.

    include_hidden:
    If `False` (default), characters with `hidden=True` in the mock
    data will be excluded. This field exists purely to demonstrate how
    a real API might expose flags for internal/experimental entities.
    """
    pass


def get_characters(
    ctx: Optional[ClientContext] = None,
    *,
    filters: Optional[CharacterFilter] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> Dict[str, Dict[str, Any]]:
    """Fetch characters from the mock backend.

    Parameters
    ----------
    ctx:
        Request context. In mock mode this is optional, but in real clients
        it may carry authentication, player id, or other headers.

    filters:
        Optional :class:`CharacterFilter` to narrow down results.

    limit:
        Max number of items to return (for pagination). If `None`, all
        matching items after `offset` are returned.

    offset:
        How many matching items to skip before collecting results.

    Returns
    -------
    dict
    """
    pass

@dataclass(frozen=True)
class ClientContext:
    """Client-side request context.

    Parameters
    ----------
    base_url:
    Optional base URL of the backend. Unused in pure mock mode, but kept
    here so the public API surface already matches a real HTTP client.

    player_id:
    Identifier of the current player (e.g., UUID or account id). Can be
    used for per-player personalization, progress tracking, etc.

    session_id:
    Identifier of the current gameplay session/run. Can be used for
    analytics, debugging, or sharding.

    locale:
    Optional locale string (e.g., `"en"`, `"ru"`). In mock mode it
    is only passed around; real clients can forward it as a header or
    query parameter.
    """
    pass

@dataclass(frozen=True)
class EmotionFilter:
    """Filter options for :func:`get_emotions`.

    Attributes
    ----------
    character_id:
    If provided, only emotions for this character id will be returned.

    mood:
    Optional mood key to filter by. This is a simple exact match against
    the emotion key (e.g., `"neutral"`, `"angry"`).
    """
    pass


def _emotion_items() -> List[Dict[str, Any]]:
    """Convert nested mock `EMOTIONS` into a flat list of emotion dicts.

    `EMOTIONS` is expected to be a mapping of::

        character_id -> {emotion_key -> label}
    """
    pass


@dataclass(frozen=True)
class EventFilter:
    """Filter options for :func:`get_events`.

    Attributes
    ----------
    day:
    Optional day index (1-based) to restrict results.

    node_id:
    Optional exact node identifier (e.g., `"D01-PA+-L00.00-initial_confusion"`).

    event_type:
    Optional node type to match (e.g., `"dialogue"`, `"exit_event"`).

    cluster_id:
    Optional cluster identifier, if the event model groups nodes
    into higher-level clusters.

    include_ai_generated:
    Reserved flag for future use where AI-generated nodes co-exist
    with scripted ones. Mock implementation ignores this flag but
    keeps it for API parity.
    """
    pass

def call_plugin(
    ctx: Optional[ClientContext],
    plugin: str,
    action: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Call a plugin action via the script client.

    Parameters
    ----------
    ctx:
        Request context (optional).

    plugin:
        Plugin name (e.g. `"labyrinth.ai_story"`).

    action:
        Action name (e.g. `"generate_ending"`).

    payload:
        Arbitrary JSON-serializable payload passed to the script.

    Returns
    -------
    dict
        The `data` part of the underlying :class:`ScriptResult`. If the
        script fails, this function raises :class:`RuntimeError`. A real
        implementation may choose a domain-specific error type instead.
    """
    pass


class GameProgress:
    """File-based progression backend (mock) with an API meant to mirror a future real backend client.

    Parameters
    ----------
    ctx:
    Optional :class:`ClientContext`. If omitted, :func:`default_context`
    is used. In mock mode this is not strictly required, but it is kept
    for future parity with a real HTTP/graph client.

    base_dir:
    Optional base directory for storing progress files. If not provided,
    it is resolved in the following order:

    1. `options.get("base_dir")` if present;
    2. environment variable `LABYRINTH_PROGRESS_DIR`;
    3. `~/.labyrinth_progress`.

    options:
    Additional configuration dictionary for future real client usage.
    Suggested permanent keys (not all used in mock mode yet):

    * `"base_dir"` - same as the `base_dir` parameter;
    * `"backend_type"` - `"file"` (default) | `"http"` | `"hybrid"`;
    * `"api_base_url"` - base URL for an HTTP backend;
    * `"auth_token"` - token for authenticated HTTP requests.
    """
    pass


@dataclass(frozen=True)
class ScriptRequest:
    """Describe a script execution request.

    Attributes
    ----------
    name:
    Fully qualified script name, e.g. `"debug.echo"` or
    `"labyrinth.ai_story.generate_ending"`.

    payload:
    Arbitrary JSON-serializable dictionary passed as input to the script.

    timeout:
    Optional soft timeout in seconds. Mock implementation ignores it but
    real clients may use it to configure HTTP timeouts or server-side
    execution limits.
    """
    pass


class AssetLocator:
    """Resolve asset directories and files based on settings.json.

    Rules:
    - All assets are expected to exist under Settings.default_local_path()/<directory>
    - No fallback to project repository paths; callers must ensure deployment.
    - file_format is a group-specific default extension (png/ogg/wav).
    """
    pass


def register_script(name: str) -> Callable[[ScriptCallable], ScriptCallable]:
    """Decorator to register a script under a given name.

    Example
    -------

    .. code-block:: python

        @register_script("debug.echo")
        def echo(payload: Dict[str, Any]) -> Dict[str, Any]:
            return {"echo": payload}
    """
    pass

class IAudioProcessor:
    """Abstract audio processing backend.

    The voice pipeline depends only on this interface. Concrete implementations
    (e.g. :class:`ResemblyzerVoskAudioProcessing`) are injected into higher-level
    components such as :class:`AudioFile` or operation classes.

    All methods raise :class:`NotImplementedError` in this base class.
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


class RealEnvelopeWriter:
    """Envelope writer that uses :class:`IAudioProcessing` and :class:`IFileSystem`.

    The real project uses a compact binary `.dat` format; this skeleton keeps
    envelopes as JSON for readability. The shape of the API matches what the
    pipeline needs: compute from audio, then write to a sidecar file.
    """
    pass


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
    pass


def _auth_headers() -> dict:
    """Build authenticated HTTP headers for OpenAI API requests.

    Retrieves OPENAI_API_KEY from environment and builds Authorization header
    along with optional organization header.

    Returns:
        Dictionary of HTTP headers including Bearer token

    Raises:
        SystemExit: If OPENAI_API_KEY is not set
    """
    pass
