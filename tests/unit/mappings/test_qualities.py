"""
Unit tests for scripts/utils/mappings/qualities.py
"""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from utils.mappings.qualities import QUALITIES


class TestQualitiesMapping:
    """Test cases for QUALITIES list."""

    def test_qualities_is_list(self):
        """Test that QUALITIES is a list."""
        assert isinstance(QUALITIES, list)

    def test_qualities_not_empty(self):
        """Test that QUALITIES list has entries."""
        assert len(QUALITIES) > 0

    def test_all_qualities_are_dicts(self):
        """Test that all items in QUALITIES are dictionaries."""
        for quality in QUALITIES:
            assert isinstance(quality, dict)

    def test_all_qualities_have_required_fields(self):
        """Test that each quality has required fields."""
        required_fields = {"id", "name", "description", "radarr", "sonarr"}

        for i, quality in enumerate(QUALITIES):
            for field in required_fields:
                assert field in quality, f"Quality {i} missing field: {field}"

    def test_quality_id_is_integer(self):
        """Test that all quality IDs are integers."""
        for i, quality in enumerate(QUALITIES):
            assert isinstance(quality["id"], int), f"Quality {i} id is not integer"
            assert quality["id"] > 0, f"Quality {i} id should be positive"

    def test_quality_name_is_string(self):
        """Test that all quality names are non-empty strings."""
        for i, quality in enumerate(QUALITIES):
            assert isinstance(quality["name"], str), f"Quality {i} name is not string"
            assert len(quality["name"]) > 0, f"Quality {i} name is empty"

    def test_quality_description_is_string(self):
        """Test that all quality descriptions are strings."""
        for i, quality in enumerate(QUALITIES):
            assert isinstance(quality["description"], str), f"Quality {i} description is not string"

    def test_radarr_sonarr_flags_are_boolean(self):
        """Test that radarr and sonarr flags are boolean."""
        for i, quality in enumerate(QUALITIES):
            assert isinstance(quality["radarr"], bool), f"Quality {i} radarr flag is not boolean"
            assert isinstance(quality["sonarr"], bool), f"Quality {i} sonarr flag is not boolean"

    def test_unique_quality_ids(self):
        """Test that all quality IDs are unique."""
        ids = [q["id"] for q in QUALITIES]
        assert len(ids) == len(set(ids)), "Quality IDs should be unique"

    def test_unique_quality_names(self):
        """Test that all quality names are unique."""
        names = [q["name"] for q in QUALITIES]
        assert len(names) == len(set(names)), "Quality names should be unique"

    def test_contains_common_qualities(self):
        """Test that QUALITIES contains common quality types."""
        quality_names = {q["name"] for q in QUALITIES}
        # Common quality names that should be present
        common_qualities = {"Bluray", "WEBDL", "Remux"}
        for common in common_qualities:
            found = any(common in name for name in quality_names)
            assert found, f"Common quality '{common}' not found"

    def test_at_least_one_radarr_quality(self):
        """Test that at least one quality supports Radarr."""
        radarr_qualities = [q for q in QUALITIES if q["radarr"]]
        assert len(radarr_qualities) > 0, "Should have at least one Radarr quality"

    def test_at_least_one_sonarr_quality(self):
        """Test that at least one quality supports Sonarr."""
        sonarr_qualities = [q for q in QUALITIES if q["sonarr"]]
        assert len(sonarr_qualities) > 0, "Should have at least one Sonarr quality"

    def test_quality_resolution_patterns(self):
        """Test that quality names follow expected patterns."""
        quality_names = {q["name"] for q in QUALITIES}
        # Most qualities should mention resolution
        resolution_keywords = {"720p", "1080p", "2160p", "480p", "360p", "Disk"}
        qualities_with_resolution = any(
            any(kw in name for kw in resolution_keywords)
            for name in quality_names
        )
        assert qualities_with_resolution, "Quality names should include resolution information"

    @pytest.mark.parametrize("service", ["radarr", "sonarr"])
    def test_service_specific_qualities_exist(self, service):
        """Test that specific qualities exist for each service."""
        service_flag = service
        service_qualities = [q for q in QUALITIES if q.get(service_flag)]
        assert len(service_qualities) > 0, f"No qualities found for {service}"
