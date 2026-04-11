def load_manifest(manifest_path: Path) -> int:
    """
    Load and validate a plugin manifest.
    
    :param manifest_path: Path to manifest JSON file
    :returns: PluginManifest object
    :raises RuntimeError: If manifest is invalid
    """
    pass


def load_plugin(manifest_path: Path) -> Tuple[PluginManifest, ScriptEngine]:
    """
    Load a plugin from its manifest.
    
    :param manifest_path: Path to manifest JSON file
    :returns: Tuple of (manifest, engine)
    :raises ManifestError: If manifest or script is invalid
    """
    pass


@dataclass
class StartupResult:
    """
    Container for startup script outcomes.

    This type is reserved for potential future extensions where the startup
    sequence may produce additional artifacts (for example, log records or
    auxiliary state to be consumed by the UI). It currently wraps a variable
    mapping and optional structured logs.

    :ivar dict vars: Arbitrary key/value mapping produced by the startup JS pipeline.
    :ivar list[dict] logs: Optional list of structured log entries emitted by the scripting
        layer. The exact shape of each entry is intentionally flexible to
        avoid coupling to a specific JS logger format.
    """

    vars: Dict[str, Any]
    logs: Optional[list[dict]] = None


class ScriptingApi:
    """
    Game-facing scripting orchestrator (JS-only manager).

    Responsibilities:
      - Load a user script OR fall back to the default JS script.
      - Construct a strict class `Context` from game-provided data.
      - Invoke a specific JS hook and return validated results.

    This class intentionally does not provide Python-side defaults for content;
    if JS fails to produce a valid result, an exception is raised after a single
    fallback attempt to the built-in script.
    """

    def __init__(self, scripts_root: Optional[Path] = None, default_init_script: Optional[Path] = None):
        """
        Create a ScriptingApi bound to a script root and default entry.

        :param scripts_root: Root directory where user-provided scripts live. When omitted,
            defaults to the internal `defaults` directory next to this module.
        :type scripts_root: pathlib.Path | None
        :param default_init_script: Explicit path to the built-in initialization JS script. When
            omitted, uses `group.js` from the internal `defaults` directory.
        :type default_init_script: pathlib.Path | None
        """
        pass

    def _load_js(self, script_path: Path):
        """
        Load a JS file into the engine with a minimal manifest.

        The manifest is synthesized to expose the `characters` capability
        from the provided file.

        :param script_path: Absolute or relative path to the JS source file to load. Must exist.
        :type script_path: pathlib.Path
        :raises FileNotFoundError: If the path does not exist.
        """
        pass

    @staticmethod
    def _default_context(
            vars_payload: Dict[str, Any],
            rng_seed: int = 12345,
            time_budget_ms: int = 200,
    ) -> Context:
        """
        Construct a strict class `Context` for startup hooks.

        The returned class `Context` is intentionally minimal and does not include
        dialogue-specific values. Only the state/vars payload and execution constraints
        (seed and budget) are set.

        :param vars_payload: Mapping passed directly to class `State` as `vars`.
        :type vars_payload: dict[str, Any]
        :param rng_seed: Deterministic random seed visible to the JS layer.
        :type rng_seed: int
        :param time_budget_ms: Soft time budget for the hook (milliseconds).
        :type time_budget_ms: int
        :returns: A fully populated class `Context` suitable for the `characters` hook.
        :rtype: game.scripting.types.Context
        """
        pass

    @staticmethod
    def _extract_characters(result: ScriptResult) -> Dict[str, Dict[str, Any]]:
        """
        Validate and extract the `characters` mapping from a result.

        This function is strict by design: it enforces types for each nesting level and
        raises class `ScriptRuntimeError` on any mismatch instead of applying implicit defaults.

        :param result: Script result returned by the JS hook.
        :type result: game.scripting.types.ScriptResult
        :returns: Mapping of character canonical name to an attribute dictionary as produced by JS.
        :rtype: dict[str, dict[str, Any]]
        :raises game.scripting.errors.ScriptRuntimeError: If `state_updates`/`vars` are missing
            or of incorrect type, or if `vars.characters` is absent or not a dict, or if any entry
            is not a string key with a dict value.
        """
        pass

    def run_initialize_characters(
            self,
            characters: Dict[str, Dict[str, Any]],
            script_path: Optional[Path] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run `characters` via the JS engine with a safe fallback.

        Execution strategy:
          1. Attempt the user-provided script (when `script_path` is given).
          2. If the first attempt is absent or fails, attempt the built-in default script exactly once.
          3. Validate the returned result strictly and return the character map.

        Note: Python does not supply defaults. If all attempts fail or the payload does not validate,
        a class `ScriptRuntimeError` is raised.

        :param characters: Mapping from canonical name to a dict of character attributes
                           (bag-first; may include canonical keys and any dynamic fields).
        :type characters: dict[str, dict[str, Any]]
        :param script_path: Optional path to a custom JS script file.
        :type script_path: pathlib.Path | None
        :returns: Mapping from character canonical name to an attribute dictionary (as produced by JS).
        :rtype: dict[str, dict[str, Any]]
        :raises FileNotFoundError: If the selected script path does not exist.
        :raises ImportError: If the underlying JS engine cannot be initialized or a required plugin cannot be loaded.
        :raises game.scripting.errors.ScriptRuntimeError: On any scripting or validation failure after exhausting the fallback attempt.
        """
        pass



class DocstringTestAssets:
    """
    Durable character storage with a dynamic attribute bag and relationship impacts.

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

    CANON_KEYS = {
        "name",
        "leadership",
        "intelligence",
        "resilience",
        "description",
        "friends",
        "enemies",
    }

    def __init__(self, name: str, emotions: Emotions, stats: Mapping[str, Any]):
        """
        Store canonical identity & catalog reference; set canonical defaults (will be overridden by `stats`).
        Store dynamic attribute bag (+ includes canonical keys), and relation impacts.
        Seed bag from canonical defaults, then overlay required stats.
        :param name: Canonical character name.
        :param emotions: Emotion catalog; exposed for UI, not for logic here.
        :param stats: Initial attribute map to overlay (bag-first).
        """
        pass

    def rand(self) -> float:
        """
        Get a deterministic random number between 0 and 1.
        
        :returns: Random float in [0, 1)
        """
        pass

    def choose(self, weighted_exits: List[Dict[str, Any]]) -> str:
        """
        Choose an exit based on weights deterministically.
        
        :param weighted_exits: List of exit dicts with 'id' and 'weight'
        :returns: Selected exit id
        """
        pass

    @abstractmethod
    def call(self, hook: str, ctx: Context) -> Optional[str]:
        """
        Call a script hook with the given context.
        
        :param hook: Hook name (e.g., "on_enter", "on_choice")
        :param ctx: Context object
        :returns: ScriptResult if the hook exists and returns a value, None otherwise
        """
        pass

    def invoke(
        self,
        plugin_id: str,
        hook: str,
        ctx: Context,
    ) -> Optional[ScriptResult]:
        """
        Invoke a script hook.
        
        :param plugin_id: Plugin identifier
        :param hook: Hook name
        :param ctx: Context object
        :returns: ScriptResult or None
        """
        pass


class ScriptCallbacks(Protocol):
    """
    Protocol for script callback functions.

    Implementations provide zero or more lifecycle hooks invoked by the
    scripting engine while traversing dialogue nodes. Each hook receives a
    class `Context` describing the current situation and may return a
    class `ScriptResult` to influence engine behavior (adjust exit weights,
    mutate state, patch text, override mood) or `None` to make no changes.

    Hooks are optional; if a script does not implement a hook, the engine
    treats it as a no-op.
    """

    def on_enter(self, context: Context) -> Optional[ScriptResult]:
        """
        Called when entering a node.

        :param context: Immutable context for the current node entry.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    def before_dialogue(self, context: Context) -> Optional[ScriptResult]:
        """
        Called before dialogue is displayed to the player.

        Typical uses: last-moment text patches, mood adjustments, or flag
        toggles based on dynamic conditions.

        :param context: Immutable context for the upcoming dialogue.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    def on_choice(self, context: Context) -> Optional[ScriptResult]:
        """
        Called when presenting or evaluating a choice.

        Typical uses: adjusting exit weights/availability or mutating state
        right before selection processing.

        :param context: Immutable context for the current choice moment.
        :type context: Context
        :returns: A result to apply (weights/state/text/mood), or `None` to
            leave the engine state unchanged.
        :rtype: Optional[ScriptResult]
        """
        pass

    @staticmethod
    def after_dialogue(context: Context) -> Optional[ScriptResult]:
        """
        Increment a simple counter after dialogue is displayed.

        Updates `state.vars.lines_shown` as an example of state mutation.
        If the counter does not exist, it is initialized to 1.

        :param context: Context for the just-shown dialogue.
        :type context: Context
        :returns: ScriptResult with state update, or None on error.
        :rtype: Optional[ScriptResult]
        """
        pass

    @staticmethod
    def on_choice(context: Context) -> Optional[ScriptResult]:
        """
        Adjust exit weights when a mapping is present.

        Recognized key in `context.state.vars`:
          - `weights_adjust` (dict[str, float]): Per-exit weight adjustments.

        :param context: Context for the current choice moment.
        :type context: Context
        :returns: ScriptResult carrying weights_adjust, or None if absent/invalid.
        :rtype: Optional[ScriptResult]
        """
        pass

class Emotions:
    """
    Lightweight accessor around a mapping of emotion metadata with a JS bridge.

    The instance wraps an *in-memory* dictionary of emotion definitions and
    exposes common queries. Behavior is delegated to a JS script so that
    modders can change normalization or policy without touching Python.
    """

    def __init__(self, emotions: Mapping[str, Mapping[str, str]], js_script: Optional[Path] = None):
        """
        Store a mutable copy of the dict users pass in (we never write to the caller's object)
        :param emotions: Mapping from emotion name to its metadata. Each value must
                         at least provide keys `category` and `impact`. An optional
                         `emoji` string is supported for UI.
        :param js_script: Optional path to a JS file implementing the default behavior.
                          If omitted, `defaults/emotions.js` is used.

        :raises FileNotFoundError: if the JS file path does not exist.
        :raises UnicodeDecodeError: if the JS file cannot be decoded as UTF-8.
        :raises Exception: if the JS engine fails to load the script.
        :raises ValidationError: if the emotion map is empty.
        """
        pass

    def relation_from_emotion(self, name: str) -> str:
        """
        Ask JS which social relation an emotion implies.

        Default: use the emotion's `impact` field.

        :param name: Canonical `emotion` key.
        :returns: "friendly" | "neutral" | "hostile"
        :raises KeyError: if the emotion is unknown and JS cannot resolve it.
        """
        pass

    def tension_delta(self, name: str) -> float:
        """
        Ask JS how this emotion should shift group tension.

        Default mapping (JS): positive=-0.01, neutral=0.0, complex=+0.015, negative=+0.02.

        :param name: Canonical `emotion` key.
        :returns: Float delta to *add* to the current tension.
        :raises KeyError: if the emotion is unknown and JS cannot resolve it.
        """
        pass


class Events:
    """
    Validate events against a declarative contract and delegate semantics to JS.

    This class is intentionally *state-light*: it does not store or mutate
    event lists. Each method call operates on the input you provide and returns
    derived values (typed events or effects).

    The JavaScript file must export a single function with the signature::

        process_event(ctxJson, eventJson, metadataJson) -> JSON string

    where each argument is a JSON-encoded string, and the return value is a JSON
    string with an object like `{"effects": [...]}`. Effects are engine-agnostic
    dictionaries that your host system applies (e.g., "enter", "say", "env.set").

    :param metadata_json: Declarative contract specifying required/optional fields for each event type. Example:
                              {
                                  "enter": {"required_fields": ["character"], "optional_fields": []},
                                  "dialogue": {"required_fields": ["character","mood","text"], "optional_fields": ["to"]},
                                  ...
                              }
    :param js_script: Optional path to the JavaScript semantics file. If omitted, `defaults/events.js` is used.
    :raises TypeError: If `metadata_json` is not a dict.
    :raises FileNotFoundError: If the JS script path does not exist.
    :raises UnicodeDecodeError: If the JS file cannot be decoded as UTF-8.
    :raises Exception: Any error raised by the underlying JS engine load.
    """

    def __init__(self, metadata_json: Dict[str, Any], js_script: Optional[Path] = None):
        """Initialize the Events engine with metadata and optional custom JS script.

        Normalizes the metadata structure and loads the JavaScript validation/semantics
        engine for processing event payloads.

        Args:
            metadata_json: Event type metadata dictionary
            js_script: Optional path to a custom JavaScript semantics file

        Raises:
            TypeError: If metadata_json is not a dict
            FileNotFoundError: If the JS script path doesn't exist
            UnicodeDecodeError: If the JS file cannot be decoded
        """
        pass

    def validate_events(self, events_json: Any) -> Tuple[bool, List[Tuple[int, str]]]:
        """
        Validate an events payload against the metadata contract and aggregate errors.

        This validator does not `raise` for content errors; instead, it returns a tuple indicating validity
        and a list of offending item indexes with a human-readable description.

        Accepted containers:
          * list[dict] of events
          * dict with `events` (or `items`) -> list[dict]

        Validation rules (per item):
          * `event_type` must exist and be known (present in metadata).
          * All paths listed in `required_fields` must be present (supports dotted paths).
          * Optional fields are never enforced at this layer.

        Container-level errors (e.g., wrong shape) are reported with index `-1`.

        :param events_json: The events payload (list[dict] or dict with `events`/`items` list).
        :returns: `(is_valid, invalid_items)` where:
                  - `is_valid` is `True` if no errors were found,
                  - `invalid_items` is `list[ (index:int, message:str) ]` describing violations.
        """
        pass

    def process_event(self, event: Dict[str, Any], ctx_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a single event through the JS handler and return effects.

        This method validates the event, calls the JS `process_event` function,
        and extracts the effect array from the result.

        :param event: Event dictionary with at least `event_type` field.
        :param ctx_vars: Context variables to pass to JS (read-only snapshot).
        :returns: List of effect dictionaries.
        :raises ValueError: If the event is invalid.
        """
        pass

    def register_alias(self, alias: str, canonical: str):
        """
        Register or confirm an alias for a canonical name.

        :param alias: Alias to register (case-sensitive).
        :type alias: str
        :param canonical: Canonical character name to map to.
        :type canonical: str
        :raises UnknownCharacterError: If the canonical name is unknown.
        :raises DuplicateAliasError: If the alias points to a different canonical name.
        """
        pass


def default_context() -> ClientContext:
    """Return a default context suitable for simple scripts/tests.

    In real usage, callers are expected to construct their own
    :class:`ClientContext` with proper `player_id` and other fields.
    """
    pass


class Video(models.Model):
    """
    Represents a video record in the system.

    This class provides attributes to store metadata for a video, such as its title,
    language, publication date, and YouTube URL. It is designed to be used as part
    of a Django application with ORM capabilities.

    :ivar title: The title of the video.
    :type title: models.CharField
    :ivar lang: The language of the video, chosen from pre-defined options.
    :type lang: models.CharField
    :ivar date: The publication date of the video.
    :type date: models.DateField
    :ivar url: The YouTube URL of the video. A specific URL format is required as
        specified in the help text.
    :type url: models.CharField
    """
    def __str__(self):
        """
        Provides string representation for an object by concatenating `title` and a
        formatted version of `date`. The output format is 'title | dd-mm-yyyy'.

        :return: A string combining the `title` attribute and the `date` attribute
            formatted as 'dd-mm-yyyy'.
        :rtype: str
        """
        pass


class CustomUrl(models.Model):
    """
    Represents a custom URL model with title, slug, language, and redirect URL.

    The CustomUrl class is used to define a model for a custom URL with attributes
    such as a title, slug, language specification, and a redirect URL. It also
    provides a string representation method for displaying the instance details
    as a formatted string.

    :ivar title: The title for the custom URL.
    :type title: models.CharField
    :ivar slug: The slug for the URL representation. This is displayed with a custom
        verbose name 'slug'.
    :type slug: models.CharField
    :ivar lang: The language of the custom URL. It uses predefined language choices.
    :type lang: models.CharField
    :ivar redirect_url: The redirect link associated with the custom URL. Includes
        a verbose name 'redirect link' and a help text 'redirect link to'.
    :type redirect_url: models.CharField
    """
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=50, verbose_name="slug")
    lang = models.CharField(max_length=50, choices=LANGUAGES)
    redirect_url = models.CharField(
        max_length=500,
        verbose_name="redirect link",
        help_text="redirect link to",
    )


class Partner(models.Model):
    """
    Represents a business partner entity.

    This class is used for storing information about a business partner,
    including their contact details, address, and other relevant attributes.
    It helps manage and organize data associated with a partner's profile.

    :ivar name: The name of the company.
    :type name: str
    :ivar firstname: The first name of the main contact within the company.
    :type firstname: str
    :ivar lastname: The last name of the main contact within the company.
    :type lastname: str
    :ivar email: The email address of the main contact.
    :type email: str
    :ivar phone_1: The primary phone number of the company or main contact.
    :type phone_1: str
    :ivar phone_2: An optional secondary phone number.
    :type phone_2: str
    :ivar address: The address of the company.
    :type address: str
    :ivar postal_code: The postal code of the company's address.
    :type postal_code: str
    :ivar city: The city where the company is located.
    :type city: str
    :ivar website: The URL of the company's website.
    :type website: str
    :ivar logo: The file path to the company's logo.
    :type logo: File
    :ivar type: The type of partner, selected from predefined choices.
    :type type: str
    """
    pass

class ProductCategory(models.Model):
    """
    Represents a category for a product in the system.

    This class is intended to define a category for products using a database model.
    It includes a single field to store the category name. The category name is
    represented as a string with constraints and guidelines for formatting, such as
    being lowercase and having no whitespace. The class is designed for use within
    a Django application.

    :ivar category: Defines the name of the product category. The value must be
        lowercase and have no whitespace. Example: "electricity_meters".
    :type category: str
    """
    pass


class CustomUrl(models.Model):
    """
    Represents a custom URL model with title, slug, language, and redirect URL.

    The CustomUrl class is used to define a model for a custom URL with attributes
    such as a title, slug, language specification, and a redirect URL. It also
    provides a string representation method for displaying the instance details
    as a formatted string.

    :ivar title: The title for the custom URL.
    :type title: models.CharField
    :ivar slug: The slug for the URL representation. This is displayed with a custom
        verbose name 'slug'.
    :type slug: models.CharField
    :ivar lang: The language of the custom URL. It uses predefined language choices.
    :type lang: models.CharField
    :ivar redirect_url: The redirect link associated with the custom URL. Includes
        a verbose name 'redirect link' and a help text 'redirect link to'.
    :type redirect_url: models.CharField
    """
    pass

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


class P7ZipArchiveService(IArchiveService):
    """7z-based archive service using the `py7zr` Python package.

    - `extract_zip(zip_path, dest_dir)` extracts into `dest_dir` and returns the top-level
      extracted directory if the archive produced a single directory, otherwise returns `dest_dir`.
    - `create_zip(src_dir, zip_path)` creates a 7z archive containing the direct children of `src_dir`.
      If `src_dir` is empty, an empty 7z archive is created.
    """

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> Path:
        """
        Extracts the contents of a 7z archive to a specified destination directory.

        The method ensures the destination directory exists and extracts all files
        from the given 7z archive. If the extracted archive contains a single
        top-level folder, the path to that folder is returned. Otherwise, the path
        to the destination directory is returned.

        :param zip_path: The path to the 7z archive to be extracted.
        :type zip_path: Path
        :param dest_dir: The destination directory where the archive content will
            be extracted.
        :type dest_dir: Path
        :return: The path to the top-level folder from the extracted archive if
            it contains a single directory, otherwise the path to the destination
            directory.
        :rtype: Path
        :raises OSError: If the extraction process fails due to a bad archive,
            missing password, general archive error, or I/O disturbance.
        """
        pass

    def create_zip(self, src_dir: Path, zip_path: Path):
        """
        Creates a 7z archive containing the contents of the source directory at the specified
        destination.

        This function zips the contents of the provided source directory into a .7z archive
        at the given destination path. It ensures the parent directory of the destination
        exists and handles situations where the source directory is empty by creating an
        empty archive.

        :param src_dir: The path to the source directory to be archived.
        :type src_dir: Path
        :param zip_path: The path where the 7z archive should be created.
        :type zip_path: Path
        :raises OSError: If there is an error during archive creation or I/O issues.
        """
        pass

class RealDownloadService(IDownloadService):
    """Real network download service with progress and integrity checks."""

    def download(self, url: str, dest: Path):
        """Download URL to dest with a simple text progress bar.

        - Uses Content-Length (if available) to compute percentage and MB totals.
        - If the final size is less than Content-Length, treats it as a fatal error:
          deletes the partial file and raises OSError.
        - Logs total download time in both success and failure cases.
        """
        pass

    @staticmethod
    def download_progress_bar(dest: Path, downloaded: int, expected_bytes: Optional[int], start: float, url: str) -> Optional[tuple[int, int]]:
        """
        Downloads a file from a given URL to a destination path and displays a progress bar
        during the download process. Handles network or filesystem errors gracefully, attempts
        to clean up partially downloaded files if an error occurs, and provides logging of download
        progress and any issues encountered.

        :param dest: Destination path where the downloaded file will be saved.
        :type dest: Path
        :param downloaded: The initial number of bytes already downloaded (if any).
        :type downloaded: int
        :param expected_bytes: The total expected size of the file in bytes, if known.
        :type expected_bytes: Optional[int]
        :param start: Start time for tracking download elapsed time.
        :type start: float
        :param url: The URL from which the file will be downloaded.
        :type url: str
        :return: A tuple containing the total bytes downloaded and the expected file size in bytes (if available).
        :rtype: Optional[tuple[int, int]]
        """
        pass

class VoiceoverNamer:
    """Utility responsible for constructing and parsing voiceover filenames.

    New canonical format:

        NNN.character-slug.first-words-slug.duration_ms[.hash].ext

    Example:

        023.romeo-y-cohiba.well-i-m-in-a-room.54243.wav
    """

    _RE = re.compile(
        r"^(?P<idx>\d{3,})\.(?P<char>[^.]+)\.(?P<text>[^.]+)\.(?P<dur>\d+)(?:\.(?P<hash>[0-9a-f]{6}))?\.(?P<ext>wav|ogg)$",
        re.IGNORECASE,
    )

    @staticmethod
    def slugify(s: str) -> str:
        """Normalize an arbitrary string into a lowercase hyphenated slug.

        :param s: Source string to slugify.
        :type s: str
        :returns: Slug with only `a-z0-9` and single hyphens.
        :rtype: str
        """
        pass

    def slugify_first_words(self, text: str, max_words: int = 5) -> str:
        """Create a slug from the first `max_words` tokens of `text`.

        :param text: Source phrase to shorten and slugify.
        :type text: str
        :param max_words: How many words to keep from the beginning.
        :type max_words: int
        :returns: Hyphenated slug of up to `max_words` words.
        """
        pass

    def make_name(
        self,
        idx: int,
        character: str,
        text: str,
        duration_ms: int,
        ext: str,
        hash_suffix: Optional[str] = None,
    ) -> str:
        """Construct a canonical voiceover filename.

        :param idx: 1-based index of the line in the script.
        :type idx: int
        :param character: Speaking character's display name.
        :type character: str
        :param text: Dialogue text to derive a short slug from.
        :type text: str
        :param duration_ms: Audio duration in milliseconds.
        :type duration_ms: int
        :param ext: File extension, with or without leading dot.
        :type ext: str
        :param hash_suffix: Optional short hash to disambiguate variants.
        :type hash_suffix: Optional[str]
        :returns: Canonical filename like `023.romeo-y-cohiba.hello.54243.wav`.
        :rtype: str
        """
        pass
