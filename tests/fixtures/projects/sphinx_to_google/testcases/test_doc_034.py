"""Utility functions for the scripting engine."""
from __future__ import annotations

import random
import json
from typing import Any, Dict, Callable


def deterministic_rng(seed: int) -> random.Random:
    """
    Create a deterministic random number generator.
    
    :param seed: Seed for the RNG
    :returns: Random instance with the given seed
    """
    pass


def deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge updates into base dictionary.
    
    :param base: Base dictionary
    :param updates: dict with updates
    :returns: New merged dictionary
    """
    pass


def coerce_result(obj: Any) -> dict | Callable:
    """
    Coerce script return value to a result dictionary.
    
    :param obj: Object returned from script
    :returns: Dictionary representation of the result
    """
    pass


def safe_json(obj: Any) -> str:
    """
    Safely convert an object to JSON string.
    
    :param obj: Object to convert
    :returns: JSON string representation
    """
    pass
