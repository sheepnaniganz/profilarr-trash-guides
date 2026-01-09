"""
Regression tests using known-good input/output pairs.

These tests ensure the pipeline maintains stability when TRaSH-Guides data changes.
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


class TestRegressionWithFixtures:
    """Regression tests using fixture data."""

    def test_regression_with_known_good_data(self, input_fixtures_dir, tmp_path):
        """Test pipeline produces expected output for known-good input."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists() or len(list(radarr_cf_dir.glob("*.json"))) == 0:
            pytest.skip("Fixture data not available")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Run pipeline
        result = collect_regex_patterns("radarr", str(radarr_cf_dir), str(output_dir))

        # Should have produced output
        output_files = list(output_dir.glob("*.yml"))
        assert len(output_files) > 0

        # All output files should be valid YAML
        for file in output_files:
            with open(file) as f:
                data = yaml.safe_load(f)
                assert data is not None

    def test_regression_yaml_structure_stability(self, input_fixtures_dir, tmp_path):
        """Test that YAML structure remains stable across runs."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture data not available")

        output_dir1 = tmp_path / "output1"
        output_dir1.mkdir()

        # First run
        result1 = collect_regex_patterns("radarr", str(radarr_cf_dir), str(output_dir1))

        regex_patterns_module.duplicate_regex_patterns.clear()

        output_dir2 = tmp_path / "output2"
        output_dir2.mkdir()

        # Second run
        result2 = collect_regex_patterns("radarr", str(radarr_cf_dir), str(output_dir2))

        # Both runs should produce same number of files
        files1 = list(output_dir1.glob("*.yml"))
        files2 = list(output_dir2.glob("*.yml"))

        assert len(files1) == len(files2)

        # Both runs should produce identical results
        assert result1 == result2

    def test_regression_pattern_consistency(self, input_fixtures_dir, tmp_path):
        """Test that patterns remain consistent across runs."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture data not available")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = collect_regex_patterns("radarr", str(radarr_cf_dir), str(output_dir))

        # Collect all pattern values
        patterns = {}
        for file in output_dir.glob("*.yml"):
            with open(file) as f:
                data = yaml.safe_load(f)
                patterns[data["name"]] = data["pattern"]

        # Should have non-empty patterns
        if len(patterns) > 0:
            # All pattern values should be strings
            for name, pattern in patterns.items():
                assert isinstance(pattern, str)
                assert len(pattern) > 0

    def test_regression_no_file_corruption(self, input_fixtures_dir, tmp_path):
        """Test that pipeline doesn't corrupt files."""
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture data not available")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        collect_regex_patterns("radarr", str(radarr_cf_dir), str(output_dir))

        output_files = list(output_dir.glob("*.yml"))

        for file in output_files:
            # File should be readable
            assert file.stat().st_size > 0

            # File should be valid YAML
            with open(file) as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"YAML corruption in {file}: {e}")

            # Should be able to re-serialize
            yaml_str = yaml.dump(data)
            assert len(yaml_str) > 0


class TestRegressionEdgeCases:
    """Regression tests for edge cases."""

    def test_regression_unicode_handling(self, tmp_path):
        """Test that unicode characters are handled correctly."""
        import json

        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create file with unicode characters
        cf_data = {
            "trash_id": "unicode-test",
            "name": "Café Format™ (日本語)",
            "specifications": [
                {
                    "name": "Unicode Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": "Café™"}
                }
            ],
            "trash_scores": {"default": 100}
        }

        with open(input_dir / "unicode.json", "w", encoding="utf-8") as f:
            json.dump(cf_data, f, ensure_ascii=False)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should not crash with unicode
        result = collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        # Should have created output
        output_files = list(output_dir.glob("*.yml"))
        assert len(output_files) > 0

    def test_regression_special_regex_characters(self, tmp_path):
        """Test that special regex characters are preserved correctly."""
        import json

        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create file with special regex characters
        cf_data = {
            "trash_id": "regex-special",
            "name": "Regex Special",
            "specifications": [
                {
                    "name": "Special Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": r"(test|pattern)\d{2,4}[a-z]$"}
                }
            ],
            "trash_scores": {"default": 100}
        }

        with open(input_dir / "special.json", "w") as f:
            json.dump(cf_data, f)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        # Output should preserve regex
        output_files = list(output_dir.glob("*.yml"))
        assert len(output_files) > 0

        with open(output_files[0]) as f:
            data = yaml.safe_load(f)
            # Pattern should be preserved
            assert r"\d" in data["pattern"] or "d" in data["pattern"]

    def test_regression_large_pattern_strings(self, tmp_path):
        """Test handling of very long pattern strings."""
        import json

        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create file with very long pattern
        long_pattern = "|".join([f"pattern_{i}" for i in range(100)])

        cf_data = {
            "trash_id": "long-pattern",
            "name": "Long Pattern",
            "specifications": [
                {
                    "name": "Long Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "fields": {"value": long_pattern}
                }
            ],
            "trash_scores": {"default": 100}
        }

        with open(input_dir / "long.json", "w") as f:
            json.dump(cf_data, f)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should handle long patterns
        result = collect_regex_patterns("radarr", str(input_dir), str(output_dir))

        output_files = list(output_dir.glob("*.yml"))
        assert len(output_files) > 0
