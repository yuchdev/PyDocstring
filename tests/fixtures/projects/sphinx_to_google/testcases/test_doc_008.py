"""Helper utilities for validating and filtering effects."""

from typing import Any, Dict, List, Set


def assert_effects_schema(effects: List[Dict[str, Any]], *, allowed_types: Set[str]):
    """
    Validate that all effects have required schema and only allowed types.
    
    :param effects: List of effect dictionaries
    :param allowed_types: Set of allowed effect type strings
    :raises AssertionError: If validation fails
    """
    pass


def only_type(effects: List[Dict[str, Any]], type_name: str) -> List[Dict[str, Any]]:
    """
    Filter effects to only those matching a specific type.
    
    :param effects: List of effect dictionaries
    :param type_name: Effect type to filter for
    :returns: List of matching effects
    """
    pass
