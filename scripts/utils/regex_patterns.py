import os

import yaml

from utils.file_utils import iterate_json_files
from utils.strings import get_name


regex_patterns = {
    "by_name": {},
    "by_pattern": {},
}


def _update_existing_pattern_for_service(existing_data, service, output_dir):
    """Update an existing pattern file to support multiple services."""
    existing_path = existing_data["file_path"]
    if not os.path.exists(existing_path):
        raise FileNotFoundError(f"Expected pattern file not found: {existing_path}")

    # Use the existing pattern name to preserve casing
    existing_name = existing_data["name"]

    # Remove service prefix if present (e.g., "Radarr - " or "Sonarr - ")
    # to get the base pattern name with original casing
    for svc in ["Radarr", "Sonarr"]:
        prefix = f"{svc} - "
        if existing_name.startswith(prefix):
            existing_name = existing_name[len(prefix):]
            break

    # Use the existing (original) name with preserved casing
    safe_name = existing_name
    new_path = os.path.join(output_dir, f"{safe_name}.yml")

    # Rename file if needed (from service-specific to generic name)
    if existing_path != new_path and not os.path.exists(new_path):
        os.rename(existing_path, new_path)
        # Update tracking data
        old_name = existing_data["name"]
        existing_data["file_path"] = new_path
        existing_data["name"] = safe_name
        # Update by_name dict with normalized keys
        old_key = old_name.lower()
        if old_key in regex_patterns["by_name"]:
            regex_patterns["by_name"].pop(old_key)
        regex_patterns["by_name"][safe_name.lower()] = existing_data

    # Update the file to add the new service tag
    with open(new_path, "r+", encoding="utf-8") as f:
        yml_data = yaml.safe_load(f)
        if "tags" not in yml_data:
            yml_data["tags"] = []
        if service.capitalize() not in yml_data["tags"]:
            yml_data["tags"].append(service.capitalize())
        yml_data["name"] = safe_name
        f.seek(0)
        yaml.dump(yml_data, f, sort_keys=False, allow_unicode=True)
        f.truncate()

    # Update services list in tracking
    if service.capitalize() not in existing_data["services"]:
        existing_data["services"].append(service.capitalize())

    # Update name in tracking data
    existing_data["name"] = safe_name

    print(f"Updated pattern for multiple services: {new_path}")


def _generate_unique_pattern_name(initial_name, pattern, output_dir):
    """Generate a unique pattern name if there are collisions."""
    final_name = initial_name
    counter = 1
    # Use lowercase for case-insensitive comparison
    normalized_key = final_name.lower()

    while normalized_key in regex_patterns["by_name"]:
        existing_pattern_data = regex_patterns["by_name"][normalized_key]
        if existing_pattern_data["pattern"] == pattern:
            print(f"Pattern with same name and pattern already exists: {final_name}")
            return None
        final_name = f"{initial_name} ({counter})"
        normalized_key = final_name.lower()
        counter += 1

    # Also check for case-insensitive file system collisions
    while _case_insensitive_file_exists(output_dir, f"{final_name}.yml"):
        final_name = f"{initial_name} ({counter})"
        normalized_key = final_name.lower()
        counter += 1

    return final_name


def _case_insensitive_file_exists(directory, filename):
    """Check if a file exists with case-insensitive matching."""
    if not os.path.exists(directory):
        return False

    filename_lower = filename.lower()
    for existing_file in os.listdir(directory):
        if existing_file.lower() == filename_lower:
            return True
    return False


def _create_new_pattern_file(service, pattern, final_name, output_dir):
    """Create a new pattern file."""
    yml_data = {
        "name": final_name,
        "pattern": pattern,
        "description": "",
        "tags": [service.capitalize()],
        "tests": [],
    }

    output_path = os.path.join(output_dir, f"{final_name}.yml")

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(yml_data, f, sort_keys=False, allow_unicode=True)

    # Store in dict (twice - by name and by pattern)
    # Use lowercase keys for case-insensitive lookups
    pattern_data = {
        "name": final_name,
        "pattern": pattern,
        "services": [service.capitalize()],
        "file_path": output_path,
    }
    regex_patterns["by_name"][final_name.lower()] = pattern_data
    regex_patterns["by_pattern"][pattern] = pattern_data

    print(f"Generated: {output_path}")
    return True


def _collect_regex_pattern(service, file_name, input_json, output_dir):
    """Extract and collect regex patterns from specifications."""
    for spec in input_json.get("specifications", []):
        implementation = spec.get("implementation")
        if implementation not in [
            "ReleaseTitleSpecification",
            "ReleaseGroupSpecification",
        ]:
            continue

        pattern = spec.get("fields", {}).get("value")
        if not pattern:
            print(f"No pattern found in {file_name} for {implementation}")
            continue

        spec_name = spec.get("name", "")

        # Check if this exact pattern was already seen
        if pattern in regex_patterns["by_pattern"]:
            existing_data = regex_patterns["by_pattern"][pattern]

            # If previously seen for the same service with the same regex - Skip
            if service.capitalize() in existing_data.get("services", []):
                print(f"Pattern already exists for {service}: {spec_name}")
                continue

            # If previously seen for a different service - update to support both
            _update_existing_pattern_for_service(
                existing_data, service, output_dir
            )
            continue

        # Pattern not seen before - check for name collisions
        initial_name = get_name(service, spec_name, remove_not=True)
        final_name = _generate_unique_pattern_name(initial_name, pattern, output_dir)

        if final_name:
            _create_new_pattern_file(service, pattern, final_name, output_dir)


def collect_regex_patterns(service, input_dir, output_dir):
    for _, file_stem, data in iterate_json_files(input_dir):
        _collect_regex_pattern(service, file_stem, data, output_dir)

    return regex_patterns
