"""
End-to-end tests for the complete pipeline.

Tests the entire ETL pipeline from input to output.
"""

import json
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


@pytest.fixture
def sample_input_directory(tmp_path):
    """Create a sample input directory with test data."""
    # Create directory structure
    radarr_cf_dir = tmp_path / "radarr" / "cf"
    radarr_cf_dir.mkdir(parents=True)

    # Create a sample custom format file
    cf_data = {
        "trash_id": "test-id",
        "name": "Test Format",
        "specifications": [
            {
                "name": "Test Pattern",
                "implementation": "ReleaseTitleSpecification",
                "negate": False,
                "required": True,
                "fields": {"value": r"\bTEST\b"},
            }
        ],
        "trash_scores": {"default": 100},
    }

    with open(radarr_cf_dir / "test.json", "w") as f:
        json.dump(cf_data, f)

    return tmp_path


class TestFullPipeline:
    """End-to-end tests for the complete pipeline."""

    def test_regex_patterns_pipeline(self, sample_input_directory, tmp_path):
        """Test the complete regex patterns generation pipeline."""
        input_dir = sample_input_directory / "radarr" / "cf"
        output_dir = tmp_path / "regex_patterns"
        output_dir.mkdir()

        # Run the pipeline
        result = collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        # Verify output
        assert isinstance(result, dict)
        assert len(list(output_dir.glob("*.yml"))) > 0

    def test_pipeline_output_structure(self, sample_input_directory, tmp_path):
        """Test that pipeline creates correct output structure."""
        input_dir = sample_input_directory / "radarr" / "cf"
        output_dir = tmp_path / "regex_patterns"
        output_dir.mkdir()

        collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        output_files = list(output_dir.glob("*.yml"))
        assert len(output_files) > 0

        # Check each output file
        for file in output_files:
            with open(file) as f:
                data = yaml.safe_load(f)

            # Validate structure
            assert "name" in data
            assert "pattern" in data
            assert "tags" in data
            assert "Radarr" in data["tags"]

    def test_pipeline_handles_multiple_files(self, tmp_path):
        """Test pipeline processing multiple input files."""
        regex_patterns_module.duplicate_regex_patterns.clear()

        # Create input directory with multiple files
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        for i in range(3):
            cf_data = {
                "trash_id": f"test-id-{i}",
                "name": f"Format {i}",
                "specifications": [
                    {
                        "name": f"Pattern {i}",
                        "implementation": "ReleaseTitleSpecification",
                        "fields": {"value": f"PATTERN_{i}"},
                    }
                ],
                "trash_scores": {"default": 100},
            }
            with open(input_dir / f"file_{i}.json", "w") as f:
                json.dump(cf_data, f)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        # Should have created files for each pattern
        output_files = list(output_dir.glob("*.yml"))
        assert len(output_files) == 3

    def test_pipeline_creates_valid_yaml(self, sample_input_directory, tmp_path):
        """Test that pipeline creates valid YAML files."""
        input_dir = sample_input_directory / "radarr" / "cf"
        output_dir = tmp_path / "regex_patterns"
        output_dir.mkdir()

        collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        output_files = list(output_dir.glob("*.yml"))

        for file in output_files:
            with open(file) as f:
                try:
                    data = yaml.safe_load(f)
                    assert data is not None
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {file}: {e}")

    def test_pipeline_with_both_services(self, tmp_path):
        """Test pipeline processing for both Radarr and Sonarr."""
        regex_patterns_module.duplicate_regex_patterns.clear()

        # Create input directories for both services
        for service in ["radarr", "sonarr"]:
            service_dir = tmp_path / "input" / service / "cf"
            service_dir.mkdir(parents=True)

            cf_data = {
                "trash_id": f"{service}-id",
                "name": f"{service} Format",
                "specifications": [
                    {
                        "name": f"{service} Pattern",
                        "implementation": "ReleaseTitleSpecification",
                        "fields": {"value": service.upper()},
                    }
                ],
                "trash_scores": {"default": 100},
            }
            with open(service_dir / "test.json", "w") as f:
                json.dump(cf_data, f)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Process Radarr
        radarr_result = collect_regex_patterns(
            "radarr", str(tmp_path / "input" / "radarr" / "cf"), str(output_dir)
        )
        radarr_files = len(list(output_dir.glob("Radarr*.yml")))

        # Reset global state
        regex_patterns_module.duplicate_regex_patterns.clear()

        # Process Sonarr
        sonarr_result = collect_regex_patterns(
            "sonarr", str(tmp_path / "input" / "sonarr" / "cf"), str(output_dir)
        )
        sonarr_files = len(list(output_dir.glob("Sonarr*.yml")))

        # Both should have created files
        assert radarr_files > 0
        assert sonarr_files > 0

    @pytest.mark.slow
    def test_pipeline_performance_with_many_files(self, tmp_path):
        """Test pipeline performance with many input files."""
        import time

        regex_patterns_module.duplicate_regex_patterns.clear()

        # Create many input files
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        num_files = 50
        for i in range(num_files):
            cf_data = {
                "trash_id": f"test-id-{i}",
                "name": f"Format {i}",
                "specifications": [
                    {
                        "name": f"Pattern {i}",
                        "implementation": "ReleaseTitleSpecification",
                        "fields": {"value": f"PATTERN_{i % 10}"},  # Some duplicates
                    }
                ],
                "trash_scores": {"default": 100},
            }
            with open(input_dir / f"file_{i:03d}.json", "w") as f:
                json.dump(cf_data, f)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Measure execution time
        start_time = time.time()
        result = collect_regex_patterns("radarr", str(input_dir), str(output_dir))
        execution_time = time.time() - start_time

        # Should complete reasonably quickly (adjust threshold as needed)
        assert (
            execution_time < 30
        ), f"Pipeline took {execution_time}s for {num_files} files"

    def test_pipeline_error_handling_empty_directory(self, tmp_path):
        """Test pipeline handles empty input directory gracefully."""
        input_dir = tmp_path / "empty_input"
        input_dir.mkdir()

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should not crash with empty directory
        result = collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        assert isinstance(result, dict)
        assert len(result) == 0  # Empty input = empty result

    def test_pipeline_error_handling_malformed_json(self, tmp_path):
        """Test pipeline handles malformed JSON gracefully."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create malformed JSON file
        with open(input_dir / "bad.json", "w") as f:
            f.write("{ invalid json content")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should handle error gracefully
        with pytest.raises(Exception):  # json.JSONDecodeError or similar
            collect_regex_patterns("radarr", str(input_dir), str(output_dir))
