# Unofficial TRaSH-Guides Database for Profilarr

This repository hosts [TRaSH-Guides's](https://trash-guides.info/) unofficial database for Profilarr containing:

- Regex Patterns
- Custom Formats
- Quality Profiles
- Media Management

The goal of this repository is to generate a Profilarr database based on TRaSH-Guides configuration without any changes. If you want anything custom you can commit it yourself within the Profilarr UI.

The repo will be automatically kept in sync with the TRaSH-Guides repository. A Github Action will run every day pulling the latest version of TRaSH-Guides and running the scripts committing and pushing any changes.

## Scripts

The repository a script to generate the specification based on the TRaSH-Guide data.

### Requirements

- **Python 3.13+**
- **UV** for package management - install via [official instructions](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)
- **TRaSH-Guides data** - a local clone with JSON data in `docs/json/` (not automatically cloned)

Dependencies are defined in `pyproject.toml` and managed by UV.

### Running the script

Assuming you're in the root directory of the repository you can now run:

```
uv run scripts/generate.py /path/to/trash-guides/docs/json .
```

It will clear any potentially pre-existing output and generate new output based on the provided TRaSH-Guides folder.

## Testing

This project includes automated tests to validate the integrity of generated output files.

### Running Tests

The test suite validates that:
- Every pattern referenced in custom formats exists as a regex pattern file
- Every custom format referenced in profiles exists as a custom format file

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest tests/ -v

# Run specific test files
uv run pytest tests/test_custom_formats.py -v
uv run pytest tests/test_profiles.py -v

# Run with coverage report
uv run pytest tests/ --cov=scripts --cov-report=term
```

### Test Validation

The tests ensure data integrity across the generated output:
- **Custom Format Tests** - Validates all pattern references in `custom_formats/` exist in `regex_patterns/`
- **Profile Tests** - Validates all custom format references in `profiles/` exist in `custom_formats/`

If a test fails, it will clearly indicate which files contain broken references, making it easy to identify and fix issues.

## Code Quality

This project uses **pylint** for static code analysis and quality checks.

```bash
# Install dev tools
uv sync --extra dev

# Run linting
uv run pylint scripts tests
```
