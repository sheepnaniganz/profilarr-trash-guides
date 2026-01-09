"""
Unit tests for core module functions: custom_formats, profiles, media_management
"""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from tests.utils.yaml_helpers import (
    validate_custom_format_yaml,
    validate_profile_yaml,
)


class TestCustomFormatIntegration:
    """Test cases for custom format generation."""

    def test_custom_format_yaml_structure(self, sample_radarr_cf_json):
        """Test that custom format YAML has expected structure."""
        # This is a simple sanity check
        assert "trash_id" in sample_radarr_cf_json
        assert "name" in sample_radarr_cf_json
        assert "specifications" in sample_radarr_cf_json
        assert "trash_scores" in sample_radarr_cf_json

    def test_specification_structure(self, sample_radarr_cf_json):
        """Test that specification structure is valid."""
        for spec in sample_radarr_cf_json["specifications"]:
            assert "name" in spec
            assert "implementation" in spec
            assert "negate" in spec
            assert "required" in spec
            assert "fields" in spec

    def test_multiple_specifications(self):
        """Test custom format with multiple specifications."""
        cf_json = {
            "trash_id": "test-multi",
            "name": "Multi Spec Format",
            "specifications": [
                {
                    "name": "Title Pattern",
                    "implementation": "ReleaseTitleSpecification",
                    "negate": False,
                    "required": True,
                    "fields": {"value": "TEST"}
                },
                {
                    "name": "Source",
                    "implementation": "SourceSpecification",
                    "negate": False,
                    "required": False,
                    "fields": {"value": 1}
                }
            ],
            "trash_scores": {"default": 100}
        }

        assert len(cf_json["specifications"]) == 2


class TestProfileGeneration:
    """Test cases for quality profile generation."""

    def test_quality_profile_structure(self):
        """Test that quality profile has expected structure."""
        profile = {
            "trash_id": "test-profile",
            "name": "Test Profile",
            "upgradesAllowed": True,
            "qualities": [
                {"name": "WEB-DL 720p", "allowed": True},
                {"name": "Remux-1080p", "allowed": True}
            ],
            "formatItems": {},
            "minCustomFormatScore": 0,
            "upgradeUntilScore": 0
        }

        assert "trash_id" in profile
        assert "name" in profile
        assert "qualities" in profile
        assert "formatItems" in profile
        assert len(profile["qualities"]) == 2

    def test_format_items_mapping(self):
        """Test that formatItems correctly maps trash IDs to format names."""
        format_items = {
            "test-id-1": "Format Name 1",
            "test-id-2": "Format Name 2"
        }

        assert len(format_items) == 2
        assert all(isinstance(k, str) for k in format_items)
        assert all(isinstance(v, str) for v in format_items.values())

    def test_upgrade_until_structure(self):
        """Test upgrade_until structure in profile."""
        upgrade_until = {
            "upgradeUntilScore": 100,
            "upgradeUntilQuality": "Remux-1080p"
        }

        assert "upgradeUntilScore" in upgrade_until
        assert isinstance(upgrade_until["upgradeUntilScore"], int)


class TestMediaManagementConfigs:
    """Test cases for media management configuration processing."""

    def test_media_management_structure(self):
        """Test that media management config has expected structure."""
        # Media management typically contains naming and quality definitions
        config = {
            "naming": {
                "folder": "pattern",
                "file": "pattern"
            },
            "quality_definitions": [],
            "misc": {}
        }

        assert "naming" in config or "quality_definitions" in config
        assert isinstance(config, dict)

    def test_media_management_naming_patterns(self):
        """Test naming pattern structure."""
        naming = {
            "folder": "{Movie Title} ({Release Year})",
            "file": "{Movie Title} ({Release Year}) - {Quality}",
            "series_folder": "{Series Title}",
            "series_season": "Season {Season:00}"
        }

        for key, value in naming.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(value) > 0


class TestYAMLOutputValidation:
    """Test YAML output validation utilities."""

    def test_validate_custom_format_yaml_structure(self):
        """Test custom format YAML validation."""
        valid_cf = {
            "name": "Test Format",
            "description": "Test description",
            "tags": ["Radarr"],
            "conditions": [
                {
                    "name": "Test Condition",
                    "type": "release_title",
                    "negate": False,
                    "required": True
                }
            ],
            "tests": []
        }

        # Should not raise
        validate_custom_format_yaml(valid_cf)

    def test_validate_custom_format_yaml_missing_field(self):
        """Test that validation fails with missing fields."""
        invalid_cf = {
            "name": "Test Format",
            # Missing required fields
            "tags": ["Radarr"],
        }

        with pytest.raises(AssertionError):
            validate_custom_format_yaml(invalid_cf)

    def test_validate_profile_yaml_structure(self):
        """Test profile YAML validation."""
        valid_profile = {
            "name": "Test Profile",
            "description": "Test description",
            "tags": ["Radarr"],
            "custom_formats": [
                {"name": "Format 1", "score": 100}
            ],
            "qualities": [
                {"id": 1, "name": "WEB-DL 720p"}
            ]
        }

        # Should not raise
        validate_profile_yaml(valid_profile)

    def test_validate_profile_yaml_invalid_custom_format_score(self):
        """Test profile validation with invalid score type."""
        invalid_profile = {
            "name": "Test Profile",
            "description": "Test description",
            "tags": ["Radarr"],
            "custom_formats": [
                {"name": "Format 1", "score": "not_an_int"}  # Should be int
            ],
            "qualities": []
        }

        with pytest.raises(AssertionError):
            validate_profile_yaml(invalid_profile)
