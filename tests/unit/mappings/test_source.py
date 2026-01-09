"""
Unit tests for scripts/utils/mappings/source.py
"""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from utils.mappings.source import SOURCE_MAPPING


class TestSourceMapping:
    """Test cases for SOURCE_MAPPING dictionary."""

    def test_mapping_has_required_services(self):
        """Test that mapping includes both services."""
        assert "radarr" in SOURCE_MAPPING
        assert "sonarr" in SOURCE_MAPPING

    def test_radarr_mapping_completeness(self):
        """Test that radarr mapping has expected values."""
        radarr_mapping = SOURCE_MAPPING["radarr"]
        assert len(radarr_mapping) > 0

        # Check that keys are integers
        assert all(isinstance(k, int) for k in radarr_mapping.keys())
        # Check that values are strings
        assert all(isinstance(v, str) for v in radarr_mapping.values())

    def test_sonarr_mapping_completeness(self):
        """Test that sonarr mapping has expected values."""
        sonarr_mapping = SOURCE_MAPPING["sonarr"]
        assert len(sonarr_mapping) > 0

        # Check that keys are integers
        assert all(isinstance(k, int) for k in sonarr_mapping.keys())
        # Check that values are strings
        assert all(isinstance(v, str) for v in sonarr_mapping.values())

    def test_services_have_different_mappings(self):
        """Test that radarr and sonarr have different mappings."""
        assert SOURCE_MAPPING["radarr"] != SOURCE_MAPPING["sonarr"]

    def test_radarr_specific_values(self):
        """Test radarr-specific source values."""
        radarr = SOURCE_MAPPING["radarr"]
        # Radarr should have these common values
        expected_values = {"cam", "dvd", "web_dl", "webrip", "bluray"}
        actual_values = set(radarr.values())
        assert expected_values.issubset(actual_values)

    def test_sonarr_specific_values(self):
        """Test sonarr-specific source values."""
        sonarr = SOURCE_MAPPING["sonarr"]
        # Sonarr should have these common values
        expected_values = {"web_dl", "webrip", "bluray", "dvd"}
        actual_values = set(sonarr.values())
        assert expected_values.issubset(actual_values)

    @pytest.mark.parametrize("service", ["radarr", "sonarr"])
    def test_no_duplicate_values(self, service):
        """Test that each service mapping has no duplicate values."""
        mapping = SOURCE_MAPPING[service]
        values = list(mapping.values())
        # Allow duplicates if absolutely necessary, but generally shouldn't exist
        assert len(values) == len(set(values))

    @pytest.mark.parametrize("service", ["radarr", "sonarr"])
    def test_all_keys_are_positive_integers(self, service):
        """Test that all mapping keys are positive integers."""
        mapping = SOURCE_MAPPING[service]
        for key in mapping.keys():
            assert isinstance(key, int)
            assert key > 0

    @pytest.mark.parametrize("service", ["radarr", "sonarr"])
    def test_no_empty_string_values(self, service):
        """Test that no mapping values are empty strings."""
        mapping = SOURCE_MAPPING[service]
        for value in mapping.values():
            assert len(value) > 0

    def test_mapping_lookup(self):
        """Test that mapping lookups work correctly."""
        radarr = SOURCE_MAPPING["radarr"]
        # Test a known mapping
        if 1 in radarr:
            value = radarr[1]
            assert isinstance(value, str)
            assert len(value) > 0
