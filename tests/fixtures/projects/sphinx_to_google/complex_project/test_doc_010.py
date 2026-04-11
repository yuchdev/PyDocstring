"""Base class for script engines."""

from abc import ABC, abstractmethod
from typing import Optional
from game.scripting.types import Context, ScriptResult, PluginManifest


class ScriptEngine(ABC):
    """
    Abstract base class for script execution engines.
    """
    
    def __init__(self):
        """
        Initialize the engine.
        """
        pass
    
    @abstractmethod
    def load(self, manifest: PluginManifest, script_code: str):
        """
        Load a script plugin.
        
        :param manifest: Plugin manifest
        :param script_code: Script source code
        """
        pass
    
    @abstractmethod
    def call(self, hook: str, ctx: Context) -> Optional[ScriptResult]:
        """
        Call a script hook with the given context.
        
        :param hook: Hook name (e.g., "on_enter", "on_choice")
        :param ctx: Context object
        :returns: ScriptResult if the hook exists and returns a value, None otherwise
        """
        pass
    
    @abstractmethod
    def close(self):
        """
        Clean up engine assets."""
        pass
    
    @property
    def manifest(self) -> Optional[PluginManifest]:
        """
        Get the loaded plugin manifest.
        
        :returns: PluginManifest if loaded, None otherwise
        """
        pass
