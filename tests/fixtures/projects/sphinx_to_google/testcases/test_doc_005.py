"""Pytest configuration and fixtures for scripting integration tests."""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from game.emotions import Emotions
from game.scripting.engine_js import JSEngine
from game.scripting.bridge import ScriptAPI


# Test asset paths
ASSETS_DIR = Path(__file__).parent.parent / "assets"
JSON_DIR = ASSETS_DIR / "json"
JS_DIR = ASSETS_DIR / "js"


@pytest.fixture
def rng_seed() -> int:
    """Fixed RNG seed for deterministic tests."""
    pass


@pytest.fixture
def emotions_fixture() -> Dict[str, Dict[str, str]]:
    """Minimal emotions dictionary for testing."""
    pass


@pytest.fixture
def emotions_obj(emotions_fixture: Dict[str, Dict[str, str]]) -> Emotions:
    """Emotions instance with test data."""
    pass


@pytest.fixture
def engine_js() -> JSEngine:
    """
    Fresh JSEngine instance per test with proper cleanup.
    
    Note: JSEngine instances must be closed after use to avoid resource leaks.
    """
    pass


@pytest.fixture
def script_api(rng_seed: int) -> ScriptAPI:
    """ScriptAPI instance with fixed seed for deterministic behavior."""
    pass


@pytest.fixture
def metadata_minimal() -> Dict[str, Dict[str, Any]]:
    """Minimal event metadata for testing."""
    pass


@pytest.fixture
def test_characters() -> Dict[str, Dict[str, Any]]:
    """Load test character definitions from JSON."""
    pass


@pytest.fixture
def test_emotions() -> Dict[str, Dict[str, str]]:
    """Load test emotion definitions from JSON."""
    pass


@pytest.fixture
def test_events() -> Dict[str, Any]:
    """Load test event payloads from JSON."""
    pass


@pytest.fixture
def e2e_dialog() -> Dict[str, Any]:
    """Load end-to-end test dialog from JSON."""
    pass


def load_js_asset(filename: str) -> str:
    """
    Load JavaScript code from test assets.
    
    :param filename: Name of JS file in assets/js/
    :returns: JavaScript source code
    """
    pass
