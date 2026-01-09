"""
Unit tests for scripts/utils/mappings/languages.py
"""

import sys
from pathlib import Path

import pytest
from utils.mappings.languages import LANGUAGE_MAPPING


# Add scripts directory to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))



class TestLanguageMapping:
    """Test cases for LANGUAGE_MAPPING dictionary."""

    def test_mapping_has_required_services(self):
        """Test that mapping includes both services."""
        assert "radarr" in LANGUAGE_MAPPING
        assert "sonarr" in LANGUAGE_MAPPING

    def test_radarr_mapping_not_empty(self):
        """Test that radarr language mapping has values."""
        assert len(LANGUAGE_MAPPING["radarr"]) > 0

    def test_sonarr_mapping_not_empty(self):
        """Test that sonarr language mapping has values."""
        assert len(LANGUAGE_MAPPING["sonarr"]) > 0

    def test_mapping_keys_are_integers(self):
        """Test that all mapping keys are integers (can be negative)."""
        for service in ["radarr", "sonarr"]:
            mapping = LANGUAGE_MAPPING[service]
            for key in mapping.keys():
                assert isinstance(key, int)

    def test_mapping_values_are_strings(self):
        """Test that all mapping values are non-empty strings."""
        for service in ["radarr", "sonarr"]:
            mapping = LANGUAGE_MAPPING[service]
            for value in mapping.values():
                assert isinstance(value, str)
                assert len(value) > 0

    def test_contains_common_languages(self):
        """Test that mappings include common languages."""
        common_languages = {"english", "french", "spanish", "german", "japanese"}

        for service in ["radarr", "sonarr"]:
            mapping = LANGUAGE_MAPPING[service]
            values = set(mapping.values())
            # At least most common languages should be present
            assert len(common_languages & values) > 0

    def test_contains_special_language_codes(self):
        """Test that radarr mapping includes special codes like 'any' and 'original'."""
        radarr = LANGUAGE_MAPPING["radarr"]
        # Check for special language codes
        values = set(radarr.values())
        # Usually 'any' and 'original' are special codes
        assert "any" in values or -1 in radarr

    @pytest.mark.parametrize("service", ["radarr", "sonarr"])
    def test_no_empty_string_values(self, service):
        """Test that no values are empty strings."""
        mapping = LANGUAGE_MAPPING[service]
        for value in mapping.values():
            assert len(value.strip()) > 0

    @pytest.mark.parametrize("service", ["radarr", "sonarr"])
    def test_mapping_values_are_lowercase_or_special(self, service):
        """Test that mapping values follow naming convention (lowercase with underscores)."""
        mapping = LANGUAGE_MAPPING[service]
        for key, value in mapping.items():
            # Values should be lowercase or contain underscores for compound words
            # Examples: "english", "portuguese_br"
            assert value == value.lower() or "_" in value

    def test_no_duplicate_values_in_service(self):
        """Test that each service has no duplicate language values."""
        for service in ["radarr", "sonarr"]:
            mapping = LANGUAGE_MAPPING[service]
            values = list(mapping.values())
            assert len(values) == len(set(values)), f"{service} has duplicate language values"

    def test_radarr_sonarr_have_overlap(self):
        """Test that radarr and sonarr mappings have some overlapping languages."""
        radarr_values = set(LANGUAGE_MAPPING["radarr"].values())
        sonarr_values = set(LANGUAGE_MAPPING["sonarr"].values())
        overlap = radarr_values & sonarr_values
        assert len(overlap) > 0, "Services should share common languages"
