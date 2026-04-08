"""Integration tests for full project conversion."""
import pytest
from pathlib import Path
from pydocstring.converter import convert_project


GOOGLE_SAMPLE = '''"""Sample module."""


def greet(name, greeting="Hello"):
    """Greet someone.

    Args:
        name (str): The person to greet.
        greeting (str): The greeting to use. Defaults to "Hello".

    Returns:
        str: The greeting message.

    Raises:
        ValueError: If name is empty.
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"{greeting}, {name}!"


class Calculator:
    """A simple calculator.

    Args:
        precision (int): Number of decimal places.
    """

    def __init__(self, precision=2):
        """Initialize the calculator.

        Args:
            precision (int): Number of decimal places.
        """
        self.precision = precision

    def add(self, a, b):
        """Add two numbers.

        Args:
            a (float): First number.
            b (float): Second number.

        Returns:
            float: The sum.
        """
        return round(a + b, self.precision)
'''

SPHINX_SAMPLE = '''"""Sample module."""


def greet(name, greeting="Hello"):
    """Greet someone.

    :param name: The person to greet.
    :type name: str
    :param greeting: The greeting to use. Defaults to "Hello".
    :type greeting: str
    :returns: The greeting message.
    :rtype: str
    :raises ValueError: If name is empty.
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"{greeting}, {name}!"


class Calculator:
    """A simple calculator.

    :param precision: Number of decimal places.
    :type precision: int
    """

    def __init__(self, precision=2):
        """Initialize the calculator.

        :param precision: Number of decimal places.
        :type precision: int
        """
        self.precision = precision

    def add(self, a, b):
        """Add two numbers.

        :param a: First number.
        :type a: float
        :param b: Second number.
        :type b: float
        :returns: The sum.
        :rtype: float
        """
        return round(a + b, self.precision)
'''


def test_google_to_sphinx_project(tmp_path):
    """Test converting a full project from Google to Sphinx style."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.py").write_text(GOOGLE_SAMPLE)

    result = convert_project(input_dir, target_style="sphinx", dry_run=True)
    assert result.files_processed == 1
    assert result.files_changed == 1

    converted = result.file_results[0].converted_source
    assert ":param name:" in converted
    assert ":type name: str" in converted
    assert ":returns:" in converted
    assert ":rtype: str" in converted
    assert ":raises ValueError:" in converted
    assert "Args:" not in converted


def test_sphinx_to_google_project(tmp_path):
    """Test converting a full project from Sphinx to Google style."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.py").write_text(SPHINX_SAMPLE)

    result = convert_project(input_dir, target_style="google", dry_run=True)
    assert result.files_processed == 1
    assert result.files_changed == 1

    converted = result.file_results[0].converted_source
    assert "Args:" in converted
    assert "    name (str):" in converted
    assert "Returns:" in converted
    assert "    str:" in converted
    assert "Raises:" in converted
    assert ":param" not in converted


def test_idempotent_google_to_sphinx(tmp_path):
    """Converting twice should produce same result."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.py").write_text(GOOGLE_SAMPLE)

    # First conversion
    result1 = convert_project(input_dir, target_style="sphinx", dry_run=True)
    converted1 = result1.file_results[0].converted_source

    # Write the converted source and convert again
    (input_dir / "sample.py").write_text(converted1)
    result2 = convert_project(input_dir, target_style="sphinx", dry_run=True)

    # Should not change on second pass
    assert not result2.files_changed


def test_roundtrip_google_sphinx_google(tmp_path):
    """Google -> Sphinx -> Google should preserve key information."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.py").write_text(GOOGLE_SAMPLE)

    # Google to Sphinx
    result1 = convert_project(input_dir, target_style="sphinx", dry_run=True)
    sphinx_source = result1.file_results[0].converted_source
    (input_dir / "sample.py").write_text(sphinx_source)

    # Sphinx back to Google
    result2 = convert_project(input_dir, target_style="google", dry_run=True)
    google_source = result2.file_results[0].converted_source

    # Key info should be preserved
    assert "Args:" in google_source
    assert "name (str):" in google_source
    assert "Returns:" in google_source


def test_exclude_glob(tmp_path):
    """Test that exclude globs work."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.py").write_text(GOOGLE_SAMPLE)
    (input_dir / "excluded.py").write_text(GOOGLE_SAMPLE)

    result = convert_project(
        input_dir,
        target_style="sphinx",
        exclude_globs=["excluded.py"],
        dry_run=True,
    )
    assert result.files_processed == 1


def test_nested_directories(tmp_path):
    """Test that nested directories are scanned."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    sub_dir = input_dir / "sub"
    sub_dir.mkdir()
    (input_dir / "sample.py").write_text(GOOGLE_SAMPLE)
    (sub_dir / "other.py").write_text(GOOGLE_SAMPLE)

    result = convert_project(input_dir, target_style="sphinx", dry_run=True)
    assert result.files_processed == 2
