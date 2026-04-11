"""High-level scripting orchestrator for the game.

Python only manages JS scripts (no Python-derived defaults).
If a provided JS script fails or returns an invalid result, we fall back to the
built-in default JS script. If that also fails, we raise.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

from game.scripting.engine_js import JSEngine
from game.scripting.types import Context, State, PluginManifest, ScriptResult
from game.scripting.errors import ScriptRuntimeError
from game.log_helper import logger


DEFAULTS_DIR = Path(__file__).parent / "defaults"
DEFAULT_INIT_SCRIPT = DEFAULTS_DIR / "group.js"


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

    def _ensure_engine(self) -> JSEngine:
        """
        Return a ready JS engine instance, creating it on first use.

        :returns: A live JS engine instance that can load and execute code.
        :rtype: game.scripting.engine_js.JSEngine
        """
        pass

    def close(self):
        """
        Dispose the underlying JS engine instance if it exists.

        Ensures the engine assets are released and the reference is cleared.
        This method is idempotent and safe to call multiple times.
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
