"""Host API bridge for scripts."""

import time
from typing import Any, Dict, List, Optional, Callable
from game.scripting.utils import deterministic_rng


class ScriptAPI:
    """
    Host API exposed to scripts.
    """
    
    def __init__(self,
        rng_seed: int,
        state_provider: Optional[Callable[[], Dict[str, Any]]] = None,
        state_updater: Optional[Callable[[str, Any], None]] = None,
    ):
        """
        Initialize the API.
        
        :param rng_seed: Seed for deterministic random number generation
        :param state_provider: Optional callback to get current state
        :param state_updater: Optional callback to update state
        """
        pass
    
    def log(self, level: str, message: str):
        """
        Log a message from the script.
        
        :param level: Log level (debug, info, warn, error)
        :param message: Message to log
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
    
    def get_flag(self, key: str) -> bool:
        """
        Get a flag value from the game state.
        
        :param key: Flag key
        :returns: Flag value (default False)
        """
        pass
    
    def set_flag(self, key: str, value: bool):
        """
        Set a flag value in the game state.
        
        :param key: Flag key
        :param value: Flag value
        """
        pass
    
    def get_var(self, key: str) -> Any:
        """
        Get a variable value from the game state.
        
        :param key: Variable key
        :returns: Variable value (default None)
        """
        pass
    
    def set_var(self, key: str, value: Any):
        """
        Set a variable value in the game state.
        
        :param key: Variable key
        :param value: Variable value
        """
        pass
    
    def now_ms(self) -> int:
        """
        Get elapsed time in milliseconds since script start.
        
        :returns: Milliseconds elapsed
        """
        pass
    
    def get_logs(self) -> List[Dict[str, str]]:
        """
        Get all logged messages.
        
        :returns: List of log entries
        """
        pass
