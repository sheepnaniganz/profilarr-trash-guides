"""
YAML validation utilities for testing generated output files.
"""

from pathlib import Path
from typing import Any


def validate_regex_pattern_yaml(yaml_data: dict[str, Any]) -> None:
    """Validate regex pattern YAML structure and required fields."""
    required_fields = ["name", "pattern", "description", "tags", "tests"]

    for field in required_fields:
        assert field in yaml_data, f"Missing required field: {field}"

    assert isinstance(yaml_data["name"], str), "name must be string"
    assert isinstance(yaml_data["pattern"], str), "pattern must be string"
    assert isinstance(yaml_data["description"], str), "description must be string"
    assert isinstance(yaml_data["tags"], list), "tags must be list"
    assert len(yaml_data["tags"]) > 0, "tags must not be empty"
    assert isinstance(yaml_data["tests"], list), "tests must be list"


def validate_custom_format_yaml(yaml_data: dict[str, Any]) -> None:
    """Validate custom format YAML structure and required fields."""
    required_fields = ["name", "description", "tags", "conditions", "tests"]

    for field in required_fields:
        assert field in yaml_data, f"Missing required field: {field}"

    assert isinstance(yaml_data["name"], str), "name must be string"
    assert isinstance(yaml_data["description"], str), "description must be string"
    assert isinstance(yaml_data["tags"], list), "tags must be list"
    assert len(yaml_data["tags"]) > 0, "tags must not be empty"
    assert isinstance(yaml_data["conditions"], list), "conditions must be list"
    assert isinstance(yaml_data["tests"], list), "tests must be list"

    # Validate each condition
    for i, condition in enumerate(yaml_data["conditions"]):
        assert isinstance(condition, dict), f"condition {i} must be dict"

        condition_required_fields = ["name", "type", "negate", "required"]
        for field in condition_required_fields:
            assert field in condition, f"condition {i} missing required field: {field}"

        assert isinstance(condition["name"], str), f"condition {i} name must be string"
        assert isinstance(condition["type"], str), f"condition {i} type must be string"
        assert isinstance(condition["negate"], bool), f"condition {i} negate must be bool"
        assert isinstance(condition["required"], bool), f"condition {i} required must be bool"


def validate_profile_yaml(yaml_data: dict[str, Any]) -> None:
    """Validate profile YAML structure and required fields."""
    required_fields = ["name", "description", "tags", "custom_formats", "qualities"]

    for field in required_fields:
        assert field in yaml_data, f"Missing required field: {field}"

    assert isinstance(yaml_data["name"], str), "name must be string"
    assert isinstance(yaml_data["description"], str), "description must be string"
    assert isinstance(yaml_data["tags"], list), "tags must be list"
    assert len(yaml_data["tags"]) > 0, "tags must not be empty"
    assert isinstance(yaml_data["custom_formats"], list), "custom_formats must be list"
    assert isinstance(yaml_data["qualities"], list), "qualities must be list"

    # Validate each custom format reference
    for i, cf in enumerate(yaml_data["custom_formats"]):
        assert isinstance(cf, dict), f"custom_format {i} must be dict"
        assert "name" in cf, f"custom_format {i} missing name"
        assert "score" in cf, f"custom_format {i} missing score"
        assert isinstance(cf["name"], str), f"custom_format {i} name must be string"
        assert isinstance(cf["score"], int), f"custom_format {i} score must be int"

    # Validate each quality
    for i, quality in enumerate(yaml_data["qualities"]):
        assert isinstance(quality, dict), f"quality {i} must be dict"
        assert "id" in quality, f"quality {i} missing id"
        assert "name" in quality, f"quality {i} missing name"


def validate_media_management_yaml(yaml_data: dict[str, Any]) -> None:
    """Validate media management YAML structure."""
    assert isinstance(yaml_data, dict), "media_management must be dict"


def validate_cross_reference(
    source_yaml: dict[str, Any],
    source_field: str,
    target_dir: Path,
    target_type: str = "yml"
) -> list[str]:
    """
    Validate that references in source YAML exist in target directory.

    Returns list of missing references.
    """
    missing = []

    if source_field not in source_yaml:
        return missing

    items = source_yaml[source_field]
    if not isinstance(items, list):
        return missing

    for item in items:
        if isinstance(item, dict) and "name" in item:
            ref_name = item["name"]
            ref_file = target_dir / f"{ref_name}.{target_type}"
            if not ref_file.exists():
                missing.append(str(ref_file))

    return missing


def compare_yaml_files(file1: Path, file2: Path) -> bool:
    """
    Compare two YAML files for structural equality.

    Note: This performs a deep comparison of the loaded YAML data,
    so formatting differences don't matter.
    """
    import yaml

    with open(file1) as f:
        data1 = yaml.safe_load(f)

    with open(file2) as f:
        data2 = yaml.safe_load(f)

    return data1 == data2
