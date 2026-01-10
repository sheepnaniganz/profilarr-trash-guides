"""Tests to ensure profiles reference valid custom format files."""

from pathlib import Path

import pytest
import yaml


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
PROFILES_DIR = PROJECT_ROOT / "profiles"
CUSTOM_FORMATS_DIR = PROJECT_ROOT / "custom_formats"


def get_all_profiles():
    """Get all profile YAML files."""
    if not PROFILES_DIR.exists():
        return []
    return list(PROFILES_DIR.glob("*.yml"))


@pytest.fixture(scope="module")
def available_custom_formats_file_names():
    """Fixture to load all available custom format names once."""
    if not CUSTOM_FORMATS_DIR.exists():
        return set()

    format_names = set()
    for yml_file in CUSTOM_FORMATS_DIR.glob("*.yml"):
        # Use filename without extension as format name
        format_names.add(yml_file.stem)

    return format_names


@pytest.fixture(scope="module")
def available_custom_formats_names():
    """Fixture to load all available custom format names once."""
    if not CUSTOM_FORMATS_DIR.exists():
        return set()

    format_names = set()
    for yml_file in CUSTOM_FORMATS_DIR.glob("*.yml"):
        # Read name from YAML file content
        with open(yml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and "name" in data:
                format_names.add(data["name"])

    return format_names


@pytest.mark.parametrize("profile_file", get_all_profiles())
def test_profile_custom_formats_exist(
    profile_file, available_custom_formats_file_names, available_custom_formats_names
):
    """Test that every custom format referenced in a profile exists in custom_formats."""
    with open(profile_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "custom_formats" not in data:
        pytest.skip(f"No custom_formats found in {profile_file.name}")

    missing_formats_files = []
    missing_formats_names = []

    for custom_format_ref in data["custom_formats"]:
        format_name = custom_format_ref.get("name")
        if not format_name:
            continue

        # Check if the referenced custom format exists in custom_formats
        if format_name not in available_custom_formats_file_names:
            missing_formats_files.append(format_name)

        # Check if the referenced custom format exists in custom_formats
        if format_name not in available_custom_formats_names:
            missing_formats_names.append(format_name)

    if missing_formats_files:
        pytest.fail(
            f"Profile '{profile_file.name}' references missing custom formats:\n"
            + "\n".join(f"  - {format}" for format in missing_formats_files)
        )

    if missing_formats_names:
        pytest.fail(
            f"Profile '{profile_file.name}' references missing custom formats:\n"
            + "\n".join(f"  - {format}" for format in missing_formats_names)
        )


def test_profiles_directory_exists():
    """Test that the profiles directory exists."""
    assert PROFILES_DIR.exists(), f"Profiles directory not found: {PROFILES_DIR}"


def test_custom_formats_directory_exists():
    """Test that the custom_formats directory exists."""
    assert CUSTOM_FORMATS_DIR.exists(), f"Custom formats directory not found: {CUSTOM_FORMATS_DIR}"
