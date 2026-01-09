"""
Shared pytest configuration and fixtures for profilarr-trash-guides tests.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml


@pytest.fixture
def temp_output_dirs(tmp_path):
    """Create temporary output directories for pipeline testing."""
    dirs = {
        "regex_patterns": tmp_path / "regex_patterns",
        "custom_formats": tmp_path / "custom_formats",
        "profiles": tmp_path / "profiles",
        "media_management": tmp_path / "media_management",
    }
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    return dirs


@pytest.fixture
def sample_radarr_cf_json() -> dict[str, Any]:
    """Sample Radarr custom format JSON from TRaSH-Guides."""
    return {
        "trash_id": "test-id-123",
        "name": "Test Format",
        "description": "Test custom format",
        "trash_scores": {
            "default": 100,
        },
        "specifications": [
            {
                "name": "Test Pattern",
                "implementation": "ReleaseTitleSpecification",
                "negate": False,
                "required": True,
                "fields": {
                    "value": r"\bTEST\b"
                }
            }
        ],
    }


@pytest.fixture
def sample_sonarr_cf_json() -> dict[str, Any]:
    """Sample Sonarr custom format JSON from TRaSH-Guides."""
    return {
        "trash_id": "test-id-456",
        "name": "Test Sonarr Format",
        "description": "Test Sonarr custom format",
        "trash_scores": {
            "default": 50,
        },
        "specifications": [
            {
                "name": "Sonarr Test Pattern",
                "implementation": "SourceSpecification",
                "negate": False,
                "required": False,
                "fields": {
                    "value": 1
                }
            }
        ],
    }


@pytest.fixture
def sample_regex_pattern_json() -> dict[str, Any]:
    """Sample regex pattern JSON with ReleaseTitleSpecification."""
    return {
        "name": "Sample Regex Pattern",
        "implementation": "ReleaseTitleSpecification",
        "negate": False,
        "required": True,
        "fields": {
            "value": r"\b(1080p|720p)\b"
        }
    }


@pytest.fixture
def fixtures_dir() -> Path:
    """Get path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def input_fixtures_dir(fixtures_dir: Path) -> Path:
    """Get path to input fixtures directory."""
    return fixtures_dir / "input"


@pytest.fixture
def expected_fixtures_dir(fixtures_dir: Path) -> Path:
    """Get path to expected output fixtures directory."""
    return fixtures_dir / "expected"


def create_test_cf_json(
    trash_id: str,
    name: str,
    service: str = "radarr",
    specifications: list = None,
    trash_scores: dict = None,
) -> dict[str, Any]:
    """Create a test custom format JSON."""
    return {
        "trash_id": trash_id,
        "name": name,
        "description": f"Test {name}",
        "trash_scores": trash_scores or {"default": 100},
        "specifications": specifications or [
            {
                "name": f"{name} Pattern",
                "implementation": "ReleaseTitleSpecification",
                "negate": False,
                "required": True,
                "fields": {
                    "value": f".*{name}.*"
                }
            }
        ],
    }


def create_test_quality_profile_json(
    trash_id: str,
    name: str,
    qualities: list = None,
) -> dict[str, Any]:
    """Create a test quality profile JSON."""
    return {
        "trash_id": trash_id,
        "name": name,
        "description": f"Test {name}",
        "upgradesAllowed": True,
        "minCustomFormatScore": 0,
        "upgradeUntilScore": 0,
        "upgradeUntilQuality": None,
        "qualities": qualities or [
            {
                "name": "WEB-DL",
                "tier": 1,
                "allowed": True,
            }
        ],
        "formatItems": [],
        "minFormatScore": 0,
        "cutoffFormatScore": 0,
        "language": "any",
    }


@pytest.fixture
def yaml_config():
    """Get YAML dump configuration (no aliases)."""
    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True

    return NoAliasDumper


@pytest.fixture
def load_yaml_file():
    """Factory fixture to load YAML files."""
    def _load(file_path: Path) -> dict[str, Any]:
        with open(file_path) as f:
            return yaml.safe_load(f)
    return _load


@pytest.fixture
def dump_yaml_file(yaml_config):
    """Factory fixture to dump YAML files."""
    def _dump(file_path: Path, data: dict[str, Any]) -> None:
        with open(file_path, "w") as f:
            yaml.dump(data, f, Dumper=yaml_config, default_flow_style=False, sort_keys=False)
    return _dump


@pytest.fixture(autouse=True)
def reset_module_globals():
    """Reset module-level global state between tests."""
    # This is called before each test
    yield
    # Any cleanup after test can go here
    # In particular, if any modules have global dicts that accumulate data,
    # we should reset them here to ensure test isolation
