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
    """Container for startup script outcomes.

    This type is reserved for potential future extensions where the startup
    sequence may produce additional artifacts (for example, log records or
    auxiliary state to be consumed by the UI). It currently wraps a variable
    mapping and optional structured logs.
    """
    pass


class ScriptingApi:
    """Game-facing scripting orchestrator (JS-only manager).

    Responsibilities:
    - Load a user script OR fall back to the default JS script.
    - Construct a strict class `Context` from game-provided data.
    - Invoke a specific JS hook and return validated results.

    This class intentionally does not provide Python-side defaults for content;
    if JS fails to produce a valid result, an exception is raised after a single
    fallback attempt to the built-in script.
    """
    pass



class DocstringTestAssets:
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


class ScriptCallbacks(Protocol):
    """Protocol for script callback functions.

    Implementations provide zero or more lifecycle hooks invoked by the
    scripting engine while traversing dialogue nodes. Each hook receives a
    class `Context` describing the current situation and may return a
    class `ScriptResult` to influence engine behavior (adjust exit weights,
    mutate state, patch text, override mood) or `None` to make no changes.

    Hooks are optional; if a script does not implement a hook, the engine
    treats it as a no-op.
    """
    pass

class Emotions:
    """Lightweight accessor around a mapping of emotion metadata with a JS bridge.

    The instance wraps an *in-memory* dictionary of emotion definitions and
    exposes common queries. Behavior is delegated to a JS script so that
    modders can change normalization or policy without touching Python.
    """
    pass


class Events:
    """Validate events against a declarative contract and delegate semantics to JS.

    This class is intentionally *state-light*: it does not store or mutate
    event lists. Each method call operates on the input you provide and returns
    derived values (typed events or effects).

    The JavaScript file must export a single function with the signature::

    process_event(ctxJson, eventJson, metadataJson) -> JSON string

    where each argument is a JSON-encoded string, and the return value is a JSON
    string with an object like `{"effects": [...]}`. Effects are engine-agnostic
    dictionaries that your host system applies (e.g., "enter", "say", "env.set").

    Args:
        Example (metadata_json: Declarative contract specifying required/optional fields for each event type.): { "enter": {"required_fields": ["character"], "optional_fields": []}, "dialogue": {"required_fields": ["character","mood","text"], "optional_fields": ["to"]}, ... }
        js_script: Optional path to the JavaScript semantics file. If omitted, `defaults/events.js` is used.

    Raises:
        TypeError: If `metadata_json` is not a dict.
        FileNotFoundError: If the JS script path does not exist.
        UnicodeDecodeError: If the JS file cannot be decoded as UTF-8.
        Exception: Any error raised by the underlying JS engine load.
    """
    pass


def default_context() -> ClientContext:
    """Return a default context suitable for simple scripts/tests.

    In real usage, callers are expected to construct their own
    :class:`ClientContext` with proper `player_id` and other fields.
    """
    pass


class Video(models.Model):
    """Represents a video record in the system.

    This class provides attributes to store metadata for a video, such as its title,
    language, publication date, and YouTube URL. It is designed to be used as part
    of a Django application with ORM capabilities.

    Args:
        title (models.CharField):
        lang (models.CharField):
        date (models.DateField):
        url (models.CharField):
    """
    pass


class CustomUrl(models.Model):
    """Represents a custom URL model with title, slug, language, and redirect URL.

    The CustomUrl class is used to define a model for a custom URL with attributes
    such as a title, slug, language specification, and a redirect URL. It also
    provides a string representation method for displaying the instance details
    as a formatted string.

    Args:
        title (models.CharField):
        slug (models.CharField):
        lang (models.CharField):
        redirect_url (models.CharField):
    """
    pass


class Partner(models.Model):
    """Represents a business partner entity.

    This class is used for storing information about a business partner,
    including their contact details, address, and other relevant attributes.
    It helps manage and organize data associated with a partner's profile.

    Args:
        name (str):
        firstname (str):
        lastname (str):
        email (str):
        phone_1 (str):
        phone_2 (str):
        address (str):
        postal_code (str):
        city (str):
        website (str):
        logo (File):
        type (str):
    """
    pass

class ProductCategory(models.Model):
    """Represents a category for a product in the system.

    This class is intended to define a category for products using a database model.
    It includes a single field to store the category name. The category name is
    represented as a string with constraints and guidelines for formatting, such as
    being lowercase and having no whitespace. The class is designed for use within
    a Django application.

    Args:
        category (str):
    """
    pass


class CustomUrl(models.Model):
    """Represents a custom URL model with title, slug, language, and redirect URL.

    The CustomUrl class is used to define a model for a custom URL with attributes
    such as a title, slug, language specification, and a redirect URL. It also
    provides a string representation method for displaying the instance details
    as a formatted string.

    Args:
        title (models.CharField):
        slug (models.CharField):
        lang (models.CharField):
        redirect_url (models.CharField):
    """
    pass

class IVoiceTrainingService(Protocol):
    """Protocol for voice training operations.

    Responsibilities:
    - Discover per-character training sets from a root directory.
    - Build a voice cache by computing speaker embeddings and centroids.
    - Serialize the cache to NPZ bytes, compatible with the legacy pipeline.
    """
    pass


class P7ZipArchiveService(IArchiveService):
    """7z-based archive service using the `py7zr` Python package.

    - `extract_zip(zip_path, dest_dir)` extracts into `dest_dir` and returns the top-level
    extracted directory if the archive produced a single directory, otherwise returns `dest_dir`.
    - `create_zip(src_dir, zip_path)` creates a 7z archive containing the direct children of `src_dir`.
    If `src_dir` is empty, an empty 7z archive is created.
    """
    pass

class RealDownloadService(IDownloadService):
    """Real network download service with progress and integrity checks."""
    pass

class VoiceoverNamer:
    """Utility responsible for constructing and parsing voiceover filenames.

    New canonical format:

    NNN.character-slug.first-words-slug.duration_ms[.hash].ext

    Example:
        023.romeo-y-cohiba.well-i-m-in-a-room.54243.wav
    """
    pass
