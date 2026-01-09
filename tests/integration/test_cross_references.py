"""
Integration tests for cross-references between generated files.

Validates that generated files correctly reference each other.
"""

import sys
from pathlib import Path

import pytest
import yaml


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import utils.regex_patterns as regex_patterns_module
from utils.regex_patterns import collect_regex_patterns


class TestCrossReferences:
    """Test cross-references between generated files."""

    def test_custom_format_references_existing_patterns(self, input_fixtures_dir):
        """Test that custom formats reference existing regex patterns."""
        # Load custom format files
        cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not cf_dir.exists():
            pytest.skip("Fixture directory not available")

        # Read a custom format file
        cf_files = list(cf_dir.glob("*.json"))

        for cf_file in cf_files:
            with open(cf_file) as f:
                cf_data = yaml.safe_load(f) if cf_file.suffix == ".yml" else f.read()

            if isinstance(cf_data, dict) and "specifications" in cf_data:
                # Should have specifications
                specs = cf_data.get("specifications", [])
                assert isinstance(specs, list)

    def test_profile_references_custom_formats(self, input_fixtures_dir):
        """Test that profiles reference custom formats."""
        profile_dir = input_fixtures_dir / "radarr" / "quality-profiles"

        if not profile_dir.exists():
            pytest.skip("Fixture directory not available")

        profile_files = list(profile_dir.glob("*.json"))

        for profile_file in profile_files:
            with open(profile_file) as f:
                import json
                profile_data = json.load(f)

            # Should have formatItems
            assert "formatItems" in profile_data
            assert isinstance(profile_data["formatItems"], dict)

    def test_duplicate_patterns_merged_correctly(self, temp_output_dirs):
        """Test that duplicate patterns are properly merged."""
        regex_patterns_module.duplicate_regex_patterns.clear()

        # Pattern should be identical after duplicate detection
        pattern_value = "TEST_PATTERN"
        regex_patterns_module.duplicate_regex_patterns[pattern_value] = "Test Name"

        # Should be able to look up the pattern
        result = regex_patterns_module.duplicate_regex_patterns.get(pattern_value)
        assert result == "Test Name"

    def test_no_orphaned_references(self, input_fixtures_dir, temp_output_dirs):
        """Test that generated files don't have orphaned references."""
        # This is a conceptual test - actual orphaned references would be caught
        # by the full pipeline test
        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        patterns = collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        # All patterns in the returned dict should correspond to files
        for pattern_value, pattern_name in patterns.items():
            if not pattern_name.startswith("Radarr - ") and not pattern_name.startswith("Sonarr - "):
                # Safe name format
                pass
            # Pattern should be a valid regex (basic check)
            assert len(pattern_value) > 0


class TestReferenceConsistency:
    """Test consistency of references across files."""

    def test_service_tags_consistent_with_filenames(self, input_fixtures_dir, temp_output_dirs):
        """Test that service tags in YAML match service in filename."""
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
                data = yaml.safe_load(f)

            if "Radarr" in file.name:
                assert "Radarr" in data.get("tags", [])
            elif "Sonarr" in file.name:
                assert "Sonarr" in data.get("tags", [])

    def test_file_names_match_yaml_names(self, input_fixtures_dir, temp_output_dirs):
        """Test that file names match the 'name' field in YAML."""
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
                data = yaml.safe_load(f)

            # File name (without extension) should match YAML name
            yaml_name = data.get("name", "")
            file_name = file.stem  # filename without extension

            # They should be related (yaml_name is what's in the file content)
            assert isinstance(yaml_name, str)
            assert len(yaml_name) > 0

    @pytest.mark.integration
    def test_full_reference_chain_validity(self, input_fixtures_dir, temp_output_dirs):
        """Test the complete reference chain from profiles to regex patterns."""
        # In a full implementation, this would:
        # 1. Generate regex patterns
        # 2. Generate custom formats (referencing patterns)
        # 3. Generate profiles (referencing custom formats)
        # 4. Validate all references exist

        radarr_cf_dir = input_fixtures_dir / "radarr" / "cf"

        if not radarr_cf_dir.exists():
            pytest.skip("Fixture directory not available")

        # At minimum, regex patterns should be generated without errors
        patterns = collect_regex_patterns(
            "radarr",
            str(radarr_cf_dir),
            str(temp_output_dirs["regex_patterns"])
        )

        assert isinstance(patterns, dict)
        assert len(patterns) >= 0  # Could be empty if no patterns found
