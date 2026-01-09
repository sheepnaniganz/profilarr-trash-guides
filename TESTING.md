# UV Testing Quick Reference

This project uses UV for dependency management. Testing is fully integrated with UV and `pyproject.toml`.

## Quick Start

```bash
# Setup test environment (one-time)
uv sync --extra test

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=scripts --cov-report=term
```

## Common Commands

### Run Tests by Category
```bash
# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# End-to-end tests only
uv run pytest tests/end_to_end/ -v

# Skip slow tests
uv run pytest tests/ -v -m "not slow"
```

### Debug & Coverage
```bash
# Show test output and print statements
uv run pytest tests/ -v -s

# Drop into debugger on failure
uv run pytest tests/ -v --pdb

# Generate HTML coverage report
uv run pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```

### Run Specific Tests
```bash
# Single test file
uv run pytest tests/unit/test_strings.py -v

# Single test class
uv run pytest tests/unit/test_strings.py::TestGetName -v

# Single test function
uv run pytest tests/unit/test_strings.py::TestGetName::test_radarr_prefix -v
```

## Configuration

Test dependencies and pytest configuration are defined in `pyproject.toml`:

```toml
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.10",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "regression: marks tests as regression tests",
]
```

## Performance

- All dependencies are pinned and managed by UV
- First run: ~3-5 seconds (dependencies install)
- Subsequent runs: ~0.1-0.2 seconds
- Test suite: 120 tests in 0.14 seconds

## CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`) automatically runs:
```bash
uv sync --extra test
uv run pytest tests/ -v --tb=short
uv run pytest tests/ --cov=scripts --cov-report=xml
```

On push/PR to `stable` and `main` branches with Python 3.13 and 3.14.
