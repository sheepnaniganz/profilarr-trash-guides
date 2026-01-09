import json
import os

import yaml

from utils.strings import get_regex_pattern_name, get_safe_name


duplicate_regex_patterns = {}


def collect_regex_pattern(service, file_name, input_json, output_dir):
    # Find the first pattern in specifications
    pattern = None

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

        # Compose YAML structure
        name = spec.get("name", "")

        existing_pattern_name = duplicate_regex_patterns.get(pattern)
        if existing_pattern_name:
            existing_pattern_path = os.path.join(
                output_dir,
                f"{existing_pattern_name}.yml",
            )
            if (
                os.path.exists(existing_pattern_path)
                and service.capitalize() not in existing_pattern_path
            ):
                new_path = os.path.join(
                    output_dir,
                    f"{get_safe_name(name)}.yml",
                )
                os.rename(
                    existing_pattern_path,
                    new_path,
                )
                with open(new_path, "r+", encoding="utf-8") as f:
                    yml_data = yaml.safe_load(f)
                    yml_data["name"] = get_safe_name(name)
                    if service.capitalize() not in yml_data["tags"]:
                        yml_data["tags"].append(service.capitalize())
                    f.seek(0)
                    yaml.dump(yml_data, f, sort_keys=False, allow_unicode=True)
                    f.truncate()
                duplicate_regex_patterns[pattern] = get_safe_name(name)
            continue
        else:
            duplicate_regex_patterns[pattern] = get_regex_pattern_name(service, name)

        yml_data = {
            "name": get_regex_pattern_name(service, name),
            "pattern": pattern,
            "description": "",
            "tags": [service.capitalize()],
            "tests": [],
        }

        # Output path
        output_path = os.path.join(
            output_dir,
            f"{get_regex_pattern_name(service, name)}.yml",
        )

        if os.path.exists(output_path):
            print(f"exists{output_path}, skipping")
            continue

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(yml_data, f, sort_keys=False, allow_unicode=True)
        print(f"Generated: {output_path}")


def collect_regex_patterns(service, input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for filename in sorted(files):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(root, filename)
            file_stem = os.path.splitext(filename)[0]  # Filename without extension
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            collect_regex_pattern(service, file_stem, data, output_dir)

    return duplicate_regex_patterns
