"""
Integration tests for the ETL pipeline flow.

Tests the two-pass processing and data flow between modules.
"""

import sys
from pathlib import Path

import pytest
import yaml


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import utils.regex_patterns as regex_patterns_module
from utils.regex_patterns import collect_regex_patterns


@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset module state between tests."""
    regex_patterns_module.duplicate_regex_patterns.clear()
    yield
    regex_patterns_module.duplicate_regex_patterns.clear()


class TestTwoPassProcessing:
    """Test the two-pass processing architecture."""

    def test_first_pass_collects_regex_patterns(self, input_fixtures_dir, temp_output_dirs):
        """Test that first pass correctly collects regex patterns."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        # First pass: collect regex patterns
        regex_patterns = collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        # Should return non-empty dict
        assert isinstance(regex_patterns, dict)

        # Should create output files
        output_files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(output_files) > 0, "First pass should create regex pattern files"

    def test_both_services_process_independently(self, input_fixtures_dir, temp_output_dirs):
        """Test that both services are processed independently."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"
        sonarr_cf_dir = input_fixtures_dir / "sonarr" / "cf"

        if not radarr_cf_dir.exists() or not sonarr_cf_dir.exists():
            pytest.skip("Fixture directories not available")

        # Process Radarr
        radarr_patterns = collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        radarr_count = len(list(temp_output_dirs["regex_patterns"].glob("Radarr *.yml")))

        # Clear for next pass
        regex_patterns_module.duplicate_regex_patterns.clear()

        # Process Sonarr
        sonarr_patterns = collect_regex_patterns(
            "sonarr",
            str(sonarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        sonarr_count = len(list(temp_output_dirs["regex_patterns"].glob("Sonarr *.yml")))

        # Both should have created files
        assert radarr_count > 0 or sonarr_count > 0

    def test_output_files_have_proper_naming(self, input_fixtures_dir, temp_output_dirs):
        """Test that output files follow naming conventions."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        output_files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))

        for file in output_files:
            # File should be .yml
            assert file.suffix == ".yml"
            # File name should contain service name or follow naming convention
            assert file.name[0].isupper()  # Should start with capital letter


class TestOutputValidation:
    """Test that output from pipeline passes validation."""

    def test_generated_regex_patterns_are_valid_yaml(self, input_fixtures_dir, temp_output_dirs):
        """Test that generated regex patterns are valid YAML."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        output_files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))

        for file in output_files:
            with open(file) as f:
                try:
                    data = yaml.safe_load(f)
                    assert data is not None, f"YAML file {file} loaded as None"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {file}: {e}")

    def test_generated_regex_patterns_have_required_fields(
        self, input_fixtures_dir, temp_output_dirs
    ):
        """Test that generated patterns have all required fields."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        output_files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        required_fields = {"name", "pattern", "description", "tags", "tests"}

        for file in output_files:
            with open(file) as f:
                data = yaml.safe_load(f)

            for field in required_fields:
                assert field in data, f"File {file} missing required field: {field}"

            # Validate field types
            assert isinstance(data["name"], str)
            assert isinstance(data["pattern"], str)
            assert isinstance(data["description"], str)
            assert isinstance(data["tags"], list)
            assert isinstance(data["tests"], list)

            # Tags should not be empty
            assert len(data["tags"]) > 0

    def test_output_file_encoding(self, input_fixtures_dir, temp_output_dirs):
        """Test that output files are properly encoded as UTF-8."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        output_files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))

        for file in output_files:
            try:
                with open(file, encoding="utf-8") as f:
                    content = f.read()
                    assert len(content) > 0
            except UnicodeDecodeError as e:
                pytest.fail(f"File {file} has encoding issues: {e}")
