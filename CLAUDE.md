# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AI instructions

- Don't create additional files for documentation, rather add documentation to already existing documentation places. Keep it short.
-

## Project Overview

This repository generates a Profilarr database from TRaSH-Guides data. It transforms TRaSH-Guides JSON configurations into YAML files organized by type: regex patterns, custom formats, quality profiles, and media management settings. The repository syncs daily with TRaSH-Guides via GitHub Actions.

## Core Architecture

The project consists of a single entry point script that orchestrates data transformation through several specialized utility modules:

**Main flow (scripts/generate.py):**
1. Accepts TRaSH-Guides JSON input directory and output directory as arguments
2. Creates/clears four output directories: `regex_patterns/`, `custom_formats/`, `profiles/`, `media_management/`
3. For each service (radarr, sonarr):
   - Collects regex patterns from `{service}/cf/` JSON files
   - Collects custom formats using the regex patterns as lookups
   - Collects quality profiles using custom format scoring data
4. Collects media management configurations

**Output structure:**
- `regex_patterns/`: YAML files containing regex pattern definitions
- `custom_formats/`: YAML files with scoring rules and condition specifications
- `profiles/`: YAML files with quality tiers and format scoring
- `media_management/`: YAML configurations for media management settings

In all cases the names of the filenames follow the naming convention of `${service} - ${name}.yaml`. However, if duplicates are found it's expected that the name of the file gets updated to `${name}` and tags are updated to have the overlapping services.

Input data can be found in the git-ignored folder TRaSH-Guides. No changes should be made to this folder, but it contains the expected input source in `TRaSH-Guides/docs/json`.

## Key Utility Modules

**scripts/utils/regex_patterns.py:** Extracts regex patterns from TRaSH-Guides custom format JSON files. Handles duplicate patterns by merging them across services (radarr/sonarr). Uses `duplicate_regex_patterns` dict to map regex strings to pattern names for later lookup. Output is stored in `regex_patterns/` as YAML.

**scripts/utils/custom_formats.py:** Transforms custom format specifications into Profilarr YAML. Maps TRaSH-Guides implementation types (ResolutionSpecification, SourceSpecification, etc.) to Profilarr condition types. Uses `IMPLEMENTATION_TO_TYPE_MAPPING` and `IMPLEMENTATION_TO_TAG_MAPPING` for this conversion. Handles conditional logic with negate/required flags. The generated data is put in `custom_formats/` as YAML. The generated custom formats contain conditions, these conditions link to the name of a generated regex_pattern file. i.e.:
```yaml
conditions:
- name: Radarr - 3D
  negate: false
  required: false
  type: release_title
  pattern: Radarr - 3D
```
connects to `regex_patterns/Radarr - 3D.yaml`

**scripts/utils/profiles.py:** Generates quality profiles by collecting allowed qualities and mapping custom format scores. Requires `trash_id_to_scoring_mapping` (a mapping of TRaSH-Guides IDs to their scoring rules across different profile contexts). The generated data is put in `profiles/` as YAML. The generated profiles contain custom_formats, these custom_formats link to the name a generate customer_format file. i.e.:
```yaml
custom_formats:
- name: Radarr - Anime BD Tier 01 (Top SeaDex Muxers)
  score: 1400
```
connects to `custom_formats/Radarr - Anime BD Tier 01 (Top SeaDex Muxers).yaml`

**scripts/utils/media_management.py:** Processes media management configurations from the input JSON.

**scripts/utils/mappings/:** Directory containing service-specific mappings (languages, sources, qualities, release types, indexer flags, quality modifiers) that translate TRaSH-Guides field values to Profilarr equivalents. These mappings are keyed by service name ("radarr" or "sonarr").

**scripts/utils/strings.py:** Utility functions for name transformation and safe naming conventions.

## Running the Script

The script requires Python 3.13+ and uses UV for dependency management.

**Standard usage:**
```bash
uv run scripts/generate.py /path/to/trash-guides/docs/json .
```

**Dependencies:** markdownify, pyyaml (defined in `pyproject.toml`)

**Setup:**
1. Ensure UV is installed
2. Clone the TRaSH-Guides repository (manually; script does not clone automatically)
3. Dependencies are automatically resolved by UV from `pyproject.toml`

## Contribution Guidelines

Commit messages follow a specific format defined in CONTRIBUTING.md:
- Format: `type(component): Description`
- Types: `create`, `add`, `tweak`, `fix`
- Components: `format`, `regex`, `profile`

Example: `fix(regex): Required negation for remux pattern`

The repository maintains strict adherence to TRaSH-Guides configuration without modifications. Manual changes should be made through Profilarr to preserve standards.

## Automated Workflow

The GitHub Actions workflow (`.github/workflows/generate.yml`) runs daily at 7:31 UTC, cloning TRaSH-Guides, running the generation script, and committing any changes. It uses Python 3.14.2 with UV.

### Dependency Management

Dependencies are centrally defined in `pyproject.toml` and managed by UV:
- **Main dependencies:** pyyaml, markdownify
- **Test dependencies:** pytest, pytest-cov, pytest-mock (optional `test` extra)
- **Update automation:** Renovate automatically opens PRs for dependency updates
  - Patch and minor versions auto-merge
  - Major versions require manual review
  - Updates scheduled weekly on Monday mornings

## Testing Infrastructure

The project includes a comprehensive test suite with **120 tests** to ensure stability and catch regressions. See [TESTING.md](TESTING.md) for complete documentation.

### Running Tests with UV
```bash
# Setup test environment
uv sync --extra test

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=scripts --cov-report=term

# Run fast tests only (skip slow tests)
uv run pytest tests/ -v -m "not slow"
```
