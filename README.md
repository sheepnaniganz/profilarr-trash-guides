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

This project includes a comprehensive test suite with **120 tests** to ensure functionality remains stable. See [TESTING.md](TESTING.md) for complete testing documentation.

### Quick Test Run
```bash
# Using UV (recommended)
uv sync --extra test
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=scripts --cov-report=term

# Skip slow tests
uv run pytest tests/ -v -m "not slow"
```

### Test Coverage
- **Unit tests** (93) - String utilities, mappings, regex extraction
- **Integration tests** (13) - Pipeline flow and cross-references
- **End-to-end tests** (14) - Full pipeline execution and regression testing

For detailed testing guide, see [TESTING.md](TESTING.md).

## Code Quality

This project uses **pylint** for static code analysis and quality checks.

```bash
# Install linting tools
uv sync --extra lint

# Run linting
uv run pylint scripts tests

# Setup pre-commit hooks
pre-commit install
pre-commit run --all-files
```

For detailed linting guide, see [FORMATTING.md](FORMATTING.md).
