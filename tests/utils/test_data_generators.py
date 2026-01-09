"""
Test data generators for creating synthetic test data.
"""

from typing import Any


def create_test_regex_pattern_spec(
    name: str = "Test Pattern",
    implementation: str = "ReleaseTitleSpecification",
    pattern: str = "TEST",
    negate: bool = False,
    required: bool = True,
) -> dict[str, Any]:
    """Create a test regex pattern specification."""
    return {
        "name": name,
        "implementation": implementation,
        "negate": negate,
        "required": required,
        "fields": {
            "value": pattern
        }
    }


def create_test_source_spec(
    name: str = "Source Spec",
    value: int = 1,
    negate: bool = False,
    required: bool = False,
) -> dict[str, Any]:
    """Create a test source specification."""
    return {
        "name": name,
        "implementation": "SourceSpecification",
        "negate": negate,
        "required": required,
        "fields": {
            "value": value
        }
    }


def create_test_custom_format_json(
    trash_id: str = "test-id",
    name: str = "Test Format",
    service: str = "radarr",
    specifications: list[dict[str, Any]] | None = None,
    trash_scores: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Create a test custom format JSON."""
    if specifications is None:
        specifications = [create_test_regex_pattern_spec()]

    if trash_scores is None:
        trash_scores = {"default": 100}

    return {
        "trash_id": trash_id,
        "name": name,
        "description": f"Test {name}",
        "trash_scores": trash_scores,
        "specifications": specifications,
    }


def create_test_quality_profile_json(
    trash_id: str = "test-profile",
    name: str = "Test Profile",
    format_items: dict[str, str] | None = None,
    qualities: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a test quality profile JSON."""
    if format_items is None:
        format_items = {}

    if qualities is None:
        qualities = [
            {
                "name": "WEB-DL 720p",
                "allowed": True
            },
            {
                "name": "Remux-1080p",
                "allowed": True
            }
        ]

    return {
        "trash_id": trash_id,
        "name": name,
        "description": f"Test {name}",
        "upgradesAllowed": True,
        "minCustomFormatScore": 0,
        "upgradeUntilScore": 0,
        "upgradeUntilQuality": None,
        "formatItems": format_items,
        "qualities": qualities,
        "minFormatScore": 0,
        "cutoffFormatScore": 0,
        "language": "any"
    }


def create_test_quality(
    name: str = "WEB-DL 720p",
    allowed: bool = True,
) -> dict[str, Any]:
    """Create a test quality entry."""
    return {
        "name": name,
        "allowed": allowed
    }


def create_parameterized_specs_for_services(
    base_name: str = "Test",
) -> dict[str, list[dict[str, Any]]]:
    """Create parameterized specifications for different implementation types."""
    return {
        "release_title": [
            create_test_regex_pattern_spec(
                name=f"{base_name} Release Title",
                implementation="ReleaseTitleSpecification",
                pattern=base_name
            )
        ],
        "source": [
            create_test_source_spec(name=f"{base_name} Source", value=1)
        ],
        "mixed": [
            create_test_regex_pattern_spec(name=f"{base_name} Title"),
            create_test_source_spec(name=f"{base_name} Source"),
        ]
    }


def create_test_expected_regex_pattern_yaml(
    name: str = "Test Pattern",
    pattern: str = "TEST",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create expected regex pattern YAML output."""
    if tags is None:
        tags = ["Radarr"]

    return {
        "name": name,
        "pattern": pattern,
        "description": "",
        "tags": tags,
        "tests": []
    }


def create_test_expected_custom_format_yaml(
    name: str = "Test Format",
    tags: list[str] | None = None,
    conditions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create expected custom format YAML output."""
    if tags is None:
        tags = ["Radarr"]

    if conditions is None:
        conditions = [
            {
                "name": "Test Pattern",
                "type": "release_title",
                "negate": False,
                "required": True,
                "pattern": "Test Pattern"
            }
        ]

    return {
        "name": name,
        "description": f"Test format: {name}",
        "tags": tags,
        "conditions": conditions,
        "tests": []
    }


def create_test_expected_profile_yaml(
    name: str = "Test Profile",
    tags: list[str] | None = None,
    custom_formats: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create expected profile YAML output."""
    if tags is None:
        tags = ["Radarr"]

    if custom_formats is None:
        custom_formats = []

    return {
        "name": name,
        "description": f"Test profile: {name}",
        "tags": tags,
        "upgradesAllowed": True,
        "minCustomFormatScore": 0,
        "upgradeUntilScore": 0,
        "custom_formats": custom_formats,
        "qualities": [],
        "upgrade_until": {},
        "language": "any"
    }


class DataBuilder:
    """Builder class for creating complex test data structures.

    Not a test class - this is a utility helper for generating test data.
    """

    def __init__(self):
        self.custom_formats: dict[str, dict[str, Any]] = {}
        self.profiles: dict[str, dict[str, Any]] = {}
        self.regex_patterns: dict[str, dict[str, Any]] = {}

    def add_custom_format(
        self,
        trash_id: str,
        name: str,
        **kwargs
    ) -> "DataBuilder":
        """Add a custom format to the test data."""
        self.custom_formats[trash_id] = create_test_custom_format_json(
            trash_id=trash_id,
            name=name,
            **kwargs
        )
        return self

    def add_quality_profile(
        self,
        trash_id: str,
        name: str,
        format_items: dict[str, str] | None = None,
        **kwargs
    ) -> "DataBuilder":
        """Add a quality profile to the test data."""
        if format_items is None:
            format_items = {}

        self.profiles[trash_id] = create_test_quality_profile_json(
            trash_id=trash_id,
            name=name,
            format_items=format_items,
            **kwargs
        )
        return self

    def build(self) -> dict[str, Any]:
        """Build the complete test data structure."""
        return {
            "custom_formats": self.custom_formats,
            "profiles": self.profiles,
            "regex_patterns": self.regex_patterns,
        }
