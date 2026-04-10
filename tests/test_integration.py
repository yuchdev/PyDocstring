"""Integration tests for full project conversion."""

import importlib.util
import shutil
import sys

from tests import PROJECT_ROOT
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
    """[Integration] converter: convert_project converts a full project from Google to Sphinx style.

    Scenario: Write a Python file with Google-style docstrings and convert the project to Sphinx style.
    Boundaries: One file with function and class docstrings; all Google markers must be gone after conversion.
    On failure, first check: convert_project file discovery, rewrite_source, and Sphinx field presence.
    """
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
    """[Integration] converter: convert_project converts a full project from Sphinx to Google style.

    Scenario: Write a Python file with Sphinx-style docstrings and convert the project to Google style.
    Boundaries: One file with function and class docstrings; all Sphinx markers must be gone after conversion.
    On failure, first check: convert_project file discovery, rewrite_source, and Google section presence.
    """
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
    """[Integration] converter: converting Google to Sphinx twice produces no further changes.

    Scenario: Convert a Google-style project to Sphinx, then convert the result again; second pass is a no-op.
    Boundaries: Single file; second conversion must report zero changed files.
    On failure, first check: idempotency of rewrite_source and style detection after first conversion.
    """
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
    """[Integration] converter: Google to Sphinx to Google roundtrip preserves key documentation.

    Scenario: Convert a Google-style project to Sphinx, then convert back to Google; verify key info retained.
    Boundaries: Single file with Args, Returns sections; param names and types must survive roundtrip.
    On failure, first check: roundtrip fidelity of parser, renderer, and rewriter for both styles.
    """
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
    """[Integration] converter: convert_project respects exclude_globs to skip matching files.

    Scenario: Create two Python files and convert the project with one file excluded by glob pattern.
    Boundaries: Two files; one excluded by pattern; only one file should be processed.
    On failure, first check: convert_project exclude_globs filtering and file discovery logic.
    """
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
    """[Integration] converter: convert_project scans nested subdirectories recursively.

    Scenario: Create Python files in both a root directory and a subdirectory, then convert the project.
    Boundaries: Two files in different directory levels; both must be processed.
    On failure, first check: convert_project recursive directory traversal and files_processed count.
    """
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    sub_dir = input_dir / "sub"
    sub_dir.mkdir()
    (input_dir / "sample.py").write_text(GOOGLE_SAMPLE)
    (sub_dir / "other.py").write_text(GOOGLE_SAMPLE)

    result = convert_project(input_dir, target_style="sphinx", dry_run=True)
    assert result.files_processed == 2


# ---------------------------------------------------------------------------
# Fixture-based tests
# ---------------------------------------------------------------------------


FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "projects"


def test_fixture_google_to_sphinx_matches_expected(tmp_path):
    """[Integration] converter: convert_project output matches expected fixture files for Google-to-Sphinx.

    Scenario: Copy a fixture input directory, run Google-to-Sphinx conversion, compare with expected output.
    Boundaries: Fixture project with known input/expected output; converted files must match byte-for-byte.
    On failure, first check: fixture files in tests/fixtures/projects/google_to_sphinx and rewriter logic.
    """
    fixture_dir = FIXTURES_DIR / "google_to_sphinx" / "basic_project"
    input_dir = fixture_dir / "input"
    expected_dir = fixture_dir / "expected"

    # Copy input to tmp_path so we can rewrite in place
    work_dir = tmp_path / "work"
    shutil.copytree(input_dir, work_dir)

    result = convert_project(work_dir, target_style="sphinx")
    assert result.files_changed >= 1, "Expected at least one file to change"

    for expected_file in expected_dir.glob("*.py"):
        work_file = work_dir / expected_file.name
        assert work_file.exists(), f"Expected {work_file} to exist"
        assert work_file.read_text() == expected_file.read_text(), (
            f"Converted {expected_file.name} does not match expected output"
        )


def test_fixture_sphinx_to_google_matches_expected(tmp_path):
    """[Integration] converter: convert_project output matches expected fixture files for Sphinx-to-Google.

    Scenario: Copy a fixture input directory, run Sphinx-to-Google conversion, compare with expected output.
    Boundaries: Fixture project with known input/expected output; converted files must match byte-for-byte.
    On failure, first check: fixture files in tests/fixtures/projects/sphinx_to_google and rewriter logic.
    """
    fixture_dir = FIXTURES_DIR / "sphinx_to_google" / "basic_project"
    input_dir = fixture_dir / "input"
    expected_dir = fixture_dir / "expected"

    work_dir = tmp_path / "work"
    shutil.copytree(input_dir, work_dir)

    result = convert_project(work_dir, target_style="google")
    assert result.files_changed >= 1

    for expected_file in expected_dir.glob("*.py"):
        work_file = work_dir / expected_file.name
        assert work_file.exists()
        assert work_file.read_text() == expected_file.read_text(), (
            f"Converted {expected_file.name} does not match expected output"
        )


# ---------------------------------------------------------------------------
# Runtime __doc__ assertion tests
# ---------------------------------------------------------------------------

GOOGLE_DOC_MODULE = '''\
"""Module with Google docstrings for __doc__ testing."""


def documented_function(x: int, y: int) -> int:
    """Add two integers.

    Args:
        x (int): First operand.
        y (int): Second operand.

    Returns:
        int: The sum of x and y.

    Raises:
        TypeError: If inputs are not integers.
    """
    return x + y


class DocumentedClass:
    """A documented class.

    Args:
        value (str): The value to store.
    """

    def __init__(self, value: str) -> None:
        """Initialize with a value.

        Args:
            value (str): The value to store.
        """
        self.value = value

    def get_value(self) -> str:
        """Return the stored value.

        Returns:
            str: The stored value.
        """
        return self.value
'''


def test_google_to_sphinx_doc_attributes(tmp_path):
    """[Integration] converter: after Google-to-Sphinx conversion, __doc__ attributes reflect Sphinx style.

    Scenario: Convert a Google-style module to Sphinx, import the result, and inspect __doc__ attributes.
    Boundaries: Module with function, class, and method docstrings; all must use Sphinx fields post-conversion.
    On failure, first check: rewrite_source Sphinx output, module import, and __doc__ attribute values.
    """
    src_file = tmp_path / "doc_test_module.py"
    src_file.write_text(GOOGLE_DOC_MODULE)

    work_dir = tmp_path / "work"
    shutil.copytree(tmp_path, work_dir, ignore=shutil.ignore_patterns("work"))

    result = convert_project(work_dir, target_style="sphinx")
    assert result.files_changed >= 1

    converted_file = work_dir / "doc_test_module.py"
    assert converted_file.exists()

    # Import the rewritten module and inspect __doc__
    module_name = f"_test_g2s_{tmp_path.name}"
    spec = importlib.util.spec_from_file_location(module_name, converted_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Module __doc__ should be unchanged (just a summary)
    assert "Module with Google docstrings" in mod.__doc__

    # Function __doc__ should now use Sphinx style
    func_doc = mod.documented_function.__doc__
    assert ":param x:" in func_doc, (
        f"Expected :param x: in function __doc__, got:\n{func_doc}"
    )
    assert ":type x: int" in func_doc
    assert ":returns:" in func_doc
    assert ":rtype: int" in func_doc
    assert ":raises TypeError:" in func_doc
    # Must NOT have Google-style markers
    assert "Args:" not in func_doc
    assert "Returns:" not in func_doc

    # Class __doc__ should use Sphinx style
    cls_doc = mod.DocumentedClass.__doc__
    assert ":param value:" in cls_doc
    assert "Args:" not in cls_doc

    # Method __doc__ should use Sphinx style
    init_doc = mod.DocumentedClass.__init__.__doc__
    assert ":param value:" in init_doc

    get_doc = mod.DocumentedClass.get_value.__doc__
    assert ":returns:" in get_doc
    assert "Returns:" not in get_doc

    # Cleanup
    if module_name in sys.modules:
        del sys.modules[module_name]


SPHINX_DOC_MODULE = '''\
"""Module with Sphinx docstrings for __doc__ testing."""


def documented_function(x: int, y: int) -> int:
    """Add two integers.

    :param x: First operand.
    :type x: int
    :param y: Second operand.
    :type y: int
    :returns: The sum of x and y.
    :rtype: int
    :raises TypeError: If inputs are not integers.
    """
    return x + y


class DocumentedClass:
    """A documented class.

    :param value: The value to store.
    :type value: str
    """

    def __init__(self, value: str) -> None:
        """Initialize with a value.

        :param value: The value to store.
        :type value: str
        """
        self.value = value

    def get_value(self) -> str:
        """Return the stored value.

        :returns: The stored value.
        :rtype: str
        """
        return self.value
'''


def test_sphinx_to_google_doc_attributes(tmp_path):
    """[Integration] converter: after Sphinx-to-Google conversion, __doc__ attributes reflect Google style.

    Scenario: Convert a Sphinx-style module to Google, import the result, and inspect __doc__ attributes.
    Boundaries: Module with function, class, and method docstrings; all must use Google sections post-conversion.
    On failure, first check: rewrite_source Google output, module import, and __doc__ attribute values.
    """
    src_file = tmp_path / "doc_test_module2.py"
    src_file.write_text(SPHINX_DOC_MODULE)

    work_dir = tmp_path / "work"
    shutil.copytree(tmp_path, work_dir, ignore=shutil.ignore_patterns("work"))

    result = convert_project(work_dir, target_style="google")
    assert result.files_changed >= 1

    converted_file = work_dir / "doc_test_module2.py"
    assert converted_file.exists()

    module_name = f"_test_s2g_{tmp_path.name}"
    spec = importlib.util.spec_from_file_location(module_name, converted_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    func_doc = mod.documented_function.__doc__
    assert "Args:" in func_doc, f"Expected Args: in function __doc__, got:\n{func_doc}"
    assert "    x (int):" in func_doc
    assert "Returns:" in func_doc
    assert "    int:" in func_doc
    assert "Raises:" in func_doc
    assert ":param" not in func_doc
    assert ":type" not in func_doc
    assert ":returns:" not in func_doc

    cls_doc = mod.DocumentedClass.__doc__
    assert "Args:" in cls_doc
    assert "    value (str):" in cls_doc

    get_doc = mod.DocumentedClass.get_value.__doc__
    assert "Returns:" in get_doc
    assert ":returns:" not in get_doc

    if module_name in sys.modules:
        del sys.modules[module_name]
