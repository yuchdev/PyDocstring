"""Script registry for managing loaded engines."""

from typing import Dict, Optional, Callable, Any, List

from game.scripting.engine_base import ScriptEngine
from game.scripting.types import Context, ScriptResult


class ScriptRegistry:
    """
    Registry for managing loaded script engines.
    """
    
    def __init__(
        self,
        state_provider: Optional[Callable[[], Dict[str, Any]]] = None,
        state_updater: Optional[Callable[[str, Any], None]] = None,
    ):
        """
        Initialize the registry.
        
        :param state_provider: Optional callback to get current game state
        :param state_updater: Optional callback to update game state
        """
        pass
    
    def register(
        self,
        plugin_id: str,
        engine: ScriptEngine,
    ):
        """
        Register a loaded engine.
        
        :param plugin_id: Unique plugin identifier
        :param engine: Loaded script engine
        """
        pass
    
    def unregister(self, plugin_id: str):
        """
        Unregister and close an engine.
        
        :param plugin_id: Plugin identifier
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
    
    def get_engine(self, plugin_id: str) -> Optional[ScriptEngine]:
        """Get a registered engine.
        
        :param plugin_id: Plugin identifier
        :returns: ScriptEngine or None
        """
        pass
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin IDs.
        
        :returns: List of plugin IDs
        """
        pass
    
    def close_all(self):
        """
        Close all registered engines.
        """
        pass
