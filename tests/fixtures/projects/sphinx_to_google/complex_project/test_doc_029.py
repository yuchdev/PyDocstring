"""Helper utilities for stable JSON snapshots and comparison."""

import json
from typing import Any


def normalize_json(obj: Any) -> str:
    """
    Convert a Python object to stable, normalized JSON string.
    
    Sorts keys, uses compact format, and ensures consistent output.
    
    :param obj: Python object to serialize
    :returns: Normalized JSON string
    """
    pass


def assert_json_equal(actual: Any, expected: Any):
    """
    Assert two objects are equal after JSON normalization.
    
    Provides clear diff on mismatch.
    
    :param actual: Actual value
    :param expected: Expected value
    :raises AssertionError: If values don't match
    """
    pass
