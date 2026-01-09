import json
import os

import yaml
from markdownify import markdownify

from utils.mappings.indexer_flags import INDEXER_FLAG_MAPPING
from utils.mappings.languages import LANGUAGE_MAPPING
from utils.mappings.quality_modifiers import QUALITY_MODIFIER_MAPPING
from utils.mappings.release_type import RELEASE_TYPE_MAPPING
from utils.mappings.source import SOURCE_MAPPING
from utils.strings import get_name, get_regex_pattern_name


IMPLEMENTATION_TO_TAG_MAPPING = {
    "ReleaseTitleSpecification": "Release Title",
    "ResolutionSpecification": "Resolution",
    "SourceSpecification": "Source",
    "LanguageSpecification": "Language",
    "ReleaseGroupSpecification": "Release Group",
    "IndexerFlagSpecification": "Indexer Flag",
    "QualityModifierSpecification": "Quality Modifier",
    "ReleaseTypeSpecification": "Release Type",
}

IMPLEMENTATION_TO_TYPE_MAPPING = {
    "ReleaseTitleSpecification": "release_title",
    "ResolutionSpecification": "resolution",
    "SourceSpecification": "source",
    "LanguageSpecification": "language",
    "ReleaseGroupSpecification": "release_group",
    "IndexerFlagSpecification": "indexer_flag",
    "QualityModifierSpecification": "quality_modifier",
    "ReleaseTypeSpecification": "release_type",
}

SERVICE_TO_TRASH_GUIDES_URL = {
    "radarr": "https://trash-guides.info/Radarr/Radarr-collection-of-custom-formats",
    "sonarr": "https://trash-guides.info/Sonarr/sonarr-collection-of-custom-formats",
}


def collect_custom_format(
    service, file_name, input_json, output_dir, custom_regex_patterns
):
    conditions = []
    implementation_tags = set()
    for spec in input_json.get("specifications", []):
        condition = {
            "name": get_name(service, spec.get("name", "")),
            "negate": spec.get("negate", False),
            "required": spec.get("required", False),
            "type": IMPLEMENTATION_TO_TYPE_MAPPING.get(
                spec.get("implementation"), "unknown"
            ),
        }

        implementation = spec.get("implementation")

        implementation_tags.add(IMPLEMENTATION_TO_TAG_MAPPING[implementation])

        if implementation in ["ReleaseTitleSpecification", "ReleaseGroupSpecification"]:
            pattern = spec.get("fields", {}).get("value")
            condition["pattern"] = custom_regex_patterns.get(
                pattern, get_regex_pattern_name(service, spec.get("name", ""))
            )
        elif implementation in ["ResolutionSpecification"]:
            condition["resolution"] = f"{spec.get('fields', {}).get('value')}p"
        elif implementation in ["SourceSpecification"]:
            condition["source"] = SOURCE_MAPPING[service][
                spec.get("fields", {}).get("value")
            ]
        elif implementation in ["LanguageSpecification"]:
            # TODO: exceptLanguage
            condition["language"] = LANGUAGE_MAPPING[service][
                spec.get("fields", {}).get("value")
            ]
        elif implementation in ["IndexerFlagSpecification"]:
            condition["flag"] = INDEXER_FLAG_MAPPING[service][
                spec.get("fields", {}).get("value")
            ]
        elif implementation in ["QualityModifierSpecification"]:
            condition["qualityModifier"] = QUALITY_MODIFIER_MAPPING[service][
                spec.get("fields", {}).get("value")
            ]
        elif implementation in ["ReleaseTypeSpecification"]:
            condition["releaseType"] = RELEASE_TYPE_MAPPING[service][
                spec.get("fields", {}).get("value")
            ]
        else:
            print(f"Unrecognised implementation ({implementation}), skipping for now.")
            continue

        conditions.append(condition)

    # Compose YAML structure
    name = input_json.get("name", "")
    yml_data = {
        "name": get_name(service, name),
        "description": f"""[Custom format from TRaSH-Guides.]({SERVICE_TO_TRASH_GUIDES_URL[service]}#{file_name})

{markdownify(input_json.get('description', ''))}""".strip(),
        "tags": [service.capitalize(), *sorted(implementation_tags)],
        "conditions": conditions,
        "tests": [],
    }

    # Include in rename is currently not supported from the file system
    # It would require inserting into the DB
    # TODO: Write a script that can do this?
    # include_in_rename = input_json.get("includeCustomFormatWhenRenaming", False)
    # if include_in_rename:
    #     yml_data["metadata"] = {"includeInRename": include_in_rename}

    # Output path
    output_path = os.path.join(output_dir, f"{get_name(service, name)}.yml")
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(yml_data, f, sort_keys=False, allow_unicode=True)
    print(f"Generated: {output_path}")


def collect_custom_formats(service, input_dir, output_dir, custom_regex_patterns):
    trash_id_to_scoring_mapping = {}
    for root, _, files in os.walk(input_dir):
        for filename in sorted(files):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(root, filename)
            file_stem = os.path.splitext(filename)[0]  # Filename without extension
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            trash_id = data.get("trash_id")
            trash_scores = data.get("trash_scores", {})
            if trash_id:
                trash_id_to_scoring_mapping[trash_id] = trash_scores

            collect_custom_format(
                service, file_stem, data, output_dir, custom_regex_patterns
            )

    return trash_id_to_scoring_mapping
