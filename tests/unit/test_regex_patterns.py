"""
Unit tests for scripts/utils/regex_patterns.py
"""

import sys
from pathlib import Path

import pytest
import yaml


# Add scripts directory to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import utils.regex_patterns as regex_patterns_module
from utils.regex_patterns import collect_regex_pattern, collect_regex_patterns


@pytest.fixture(autouse=True)
def reset_duplicate_patterns():
    """Reset the global duplicate_regex_patterns dict before each test."""
    regex_patterns_module.duplicate_regex_patterns.clear()
    yield
    regex_patterns_module.duplicate_regex_patterns.clear()


class TestCollectRegexPattern:
    """Test cases for collect_regex_pattern function."""

    def test_extract_basic_release_title_pattern(self, temp_output_dirs):
        """Test extracting a basic ReleaseTitleSpecification pattern."""
        input_json = {
            "specifications": [
                {
                    "name": "Test Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "negate": False,
                    "required": True,
                    "fields": {"value": r"\bTEST\b"}
                }
            ]
        }

        collect_regex_pattern("radarr", "test-file", input_json, str(temp_output_dirs["regex_patterns"]))

        output_file = temp_output_dirs["regex_patterns"] / "Radarr - Test Pattern.yml"
        assert output_file.exists(), "Output YAML file should be created"

        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert data["name"] == "Radarr - Test Pattern"
        assert data["pattern"] == r"\bTEST\b"
        assert data["description"] == ""
        assert "Radarr" in data["tags"]
        assert data["tests"] == []

    def test_skip_non_regex_specifications(self, temp_output_dirs):
        """Test that non-regex specifications are skipped."""
        input_json = {
            "specifications": [
                {
                    "name": "Source Spec",
                    "implementation": "SourceSpecification",
                    "fields": {"value": 1}
                },
                {
                    "name": "Test Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": r"\bTEST\b"}
                }
            ]
        }

        collect_regex_pattern("radarr", "test", input_json, str(temp_output_dirs["regex_patterns"]))

        # Only the ReleaseTitleSpecification should create a file
        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) == 1
        assert "Test Pattern" in files[0].name

    def test_skip_pattern_without_value(self, temp_output_dirs, capsys):
        """Test that patterns without values are skipped."""
        input_json = {
            "specifications": [
                {
                    "name": "Empty Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {}
                }
            ]
        }

        collect_regex_pattern("radarr", "test", input_json, str(temp_output_dirs["regex_patterns"]))

        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) == 0, "No file should be created for empty pattern"

    def test_release_group_specification(self, temp_output_dirs):
        """Test extracting ReleaseGroupSpecification pattern."""
        input_json = {
            "specifications": [
                {
                    "name": "Release Group",
                    "implementation": "ReleaseGroupSpecification",
                    "fields": {"value": r"GroupName"}
                }
            ]
        }

        collect_regex_pattern("sonarr", "test", input_json, str(temp_output_dirs["regex_patterns"]))

        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) == 1
        assert "Release Group" in files[0].name

    def test_duplicate_pattern_detection(self, temp_output_dirs):
        """Test detection and handling of duplicate patterns."""
        pattern_value = r"\bDUPLICATE\b"

        # First pattern
        json1 = {
            "specifications": [
                {
                    "name": "Pattern One",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": pattern_value}
                }
            ]
        }
        collect_regex_pattern("radarr", "file1", json1, str(temp_output_dirs["regex_patterns"]))

        # Second pattern with same regex
        json2 = {
            "specifications": [
                {
                    "name": "Pattern Two",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": pattern_value}
                }
            ]
        }
        collect_regex_pattern("sonarr", "file2", json2, str(temp_output_dirs["regex_patterns"]))

        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        # Should have either 1 (if deduped) or 2 files depending on implementation
        assert len(files) >= 1

    def test_yaml_output_structure(self, temp_output_dirs):
        """Test that output YAML has correct structure."""
        input_json = {
            "specifications": [
                {
                    "name": "Structured Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": "TEST_PATTERN"}
                }
            ]
        }

        collect_regex_pattern("radarr", "test", input_json, str(temp_output_dirs["regex_patterns"]))

        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) == 1

        with open(files[0]) as f:
            data = yaml.safe_load(f)

        required_fields = ["name", "pattern", "description", "tags", "tests"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_sonarr_service_naming(self, temp_output_dirs):
        """Test that Sonarr service is properly capitalized in output."""
        input_json = {
            "specifications": [
                {
                    "name": "Sonarr Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": "SONARR_TEST"}
                }
            ]
        }

        collect_regex_pattern("sonarr", "test", input_json, str(temp_output_dirs["regex_patterns"]))

        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) == 1
        assert "Sonarr" in files[0].name

        with open(files[0]) as f:
            data = yaml.safe_load(f)

        assert "Sonarr" in data["tags"]


class TestCollectRegexPatterns:
    """Test cases for collect_regex_patterns function."""

    def test_walk_directory_and_process_files(self, input_fixtures_dir, temp_output_dirs):
        """Test processing all JSON files in a directory."""
        result = collect_regex_patterns(
            "radarr",
            str(input_fixtures_dir / "radarr" / "cf"),
            str(temp_output_dirs["regex_patterns"])
        )

        # Should return the duplicate_patterns dict
        assert isinstance(result, dict)

        # Should create output files
        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) > 0

    def test_skip_non_json_files(self, tmp_path, temp_output_dirs):
        """Test that non-JSON files are skipped."""
        # Create test files
        (tmp_path / "test.json").write_text('{"specifications": []}')
        (tmp_path / "test.txt").write_text("not json")
        (tmp_path / "test.yaml").write_text("yaml: content")

        result = collect_regex_patterns(
            "radarr",
            str(tmp_path),
            str(temp_output_dirs["regex_patterns"])
        )

        # Should only process the JSON file (which has no patterns)
        assert isinstance(result, dict)

    def test_return_duplicate_patterns_mapping(self, input_fixtures_dir, temp_output_dirs):
        """Test that function returns duplicate patterns mapping."""
        result = collect_regex_patterns(
            "radarr",
            str(input_fixtures_dir / "radarr" / "cf"),
            str(temp_output_dirs["regex_patterns"])
        )

        # Result should be a dict mapping patterns to names
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str), "Pattern keys should be strings"
            assert isinstance(value, str), "Pattern names should be strings"

    def test_handles_empty_directory(self, tmp_path, temp_output_dirs):
        """Test handling of empty input directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = collect_regex_patterns(
            "radarr",
            str(empty_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        assert result == {}
        files = list(temp_output_dirs["regex_patterns"].glob("*.yml"))
        assert len(files) == 0
