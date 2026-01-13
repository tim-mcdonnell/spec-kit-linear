# Local Development Guide

This guide shows how to iterate on Spec Kit Linear locally without publishing a release or committing to `main` first.

## 1. Clone and Switch Branches

```bash
git clone https://github.com/your-org/spec-kit-linear.git
cd spec-kit-linear
# Work on a feature branch
git checkout -b your-feature-branch
```

## 2. Set Up the Development Environment

Create an isolated environment using `uv`:

```bash
# Create & activate virtual env (uv auto-manages .venv)
uv venv
source .venv/bin/activate  # or on Windows PowerShell: .venv\Scripts\Activate.ps1

# Install project in editable mode
uv pip install -e .
```

Re-running after code edits requires no reinstall because of editable mode.

## 3. Configure Linear API Access

Set your Linear API token for local development:

```bash
export LINEAR_TOKEN="lin_api_..."
```

You can also create a `.env` file (not committed):

```
LINEAR_TOKEN=lin_api_...
```

## 4. Run the CLI Directly

You can execute the CLI via the module entrypoint:

```bash
# From repo root
python -m src.specify_cli --help
python -m src.specify_cli init demo-project --ai claude
```

Or if you have installed in editable mode:

```bash
specify --help
specify init demo-project --ai claude
```

## 5. Working with the Linear Client Library

The `src/linear/` package provides the Python client for Linear's GraphQL API.

### Quick Test

```bash
python -c "from linear import LinearClient; print('Import OK')"
```

### Interactive Testing

```python
from linear import LinearClient, LinearQueries, LinearMutations

# Initialize client (uses LINEAR_TOKEN env var)
client = LinearClient()
queries = LinearQueries(client)
mutations = LinearMutations(client)

# Test a query
team = queries.get_team("your-team-id")
print(f"Team: {team.name}")
```

## 6. Testing Template Commands

The command templates in `templates/commands/` define the behavior of slash commands. To test changes:

1. Edit the template file (e.g., `templates/commands/specify.md`)
2. Use the template with your AI assistant (Claude Code, etc.)
3. Verify the command creates/updates Linear entities correctly

## 7. Testing CI Workflows Locally

The `.woodpecker/` directory contains CI job definitions. To test locally:

```bash
# Set required environment variables
export LINEAR_TOKEN="lin_api_..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_TOKEN="ghp_..."

# Simulate what a CI job would do
# (This depends on your specific CI setup)
```

## 8. Validating linear-config.json

Ensure your configuration file is valid:

```bash
python -c "import json; json.load(open('linear-config.json'))"
```

Check against the schema:

```bash
# If you have a JSON schema validator installed
jsonschema -i linear-config.json linear-config.schema.json
```

## 9. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_linear_client.py
```

## 10. Lint and Format

```bash
# Format code
ruff format src/

# Check linting
ruff check src/

# Type checking (if configured)
mypy src/
```

## 11. Build a Wheel Locally (Optional)

Validate packaging before publishing:

```bash
uv build
ls dist/
```

## 12. Rapid Edit Loop Summary

| Action | Command |
|--------|---------|
| Run CLI directly | `python -m src.specify_cli --help` |
| Editable install | `uv pip install -e .` then `specify ...` |
| Test Linear import | `python -c "from linear import LinearClient"` |
| Run tests | `pytest` |
| Build wheel | `uv build` |

## 13. Development Workflow

### For CLI Changes (`src/specify_cli/`)

1. Make changes to `src/specify_cli/__init__.py`
2. Test with `python -m src.specify_cli [command]`
3. Verify behavior matches expected output
4. Update version in `pyproject.toml` if releasing

### For Linear Client Changes (`src/linear/`)

1. Make changes to the relevant file (`client.py`, `queries.py`, `mutations.py`)
2. Write or update tests in `tests/`
3. Test interactively with a real Linear workspace
4. Verify GraphQL queries/mutations work correctly

### For Template Changes (`templates/commands/`)

1. Edit the template markdown file
2. Test with your AI assistant
3. Verify Linear entities are created/updated correctly
4. Check for edge cases (missing data, errors, etc.)

### For CI Changes (`.woodpecker/`)

1. Edit the workflow YAML file
2. Test by triggering the workflow (add label, create webhook event)
3. Check CI logs for errors
4. Verify Linear state changes are correct

## 14. Cleaning Up

Remove build artifacts / virtual env:

```bash
rm -rf .venv dist build *.egg-info
```

## 15. Common Issues

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: linear` | Run `uv pip install -e .` |
| `LINEAR_TOKEN not set` | Export the env var or add to `.env` |
| GraphQL errors | Check token permissions in Linear settings |
| Import errors | Ensure you're in the virtual environment |
| CI job not triggering | Check webhook configuration and label names |

## 16. Next Steps

- Review the [AGENTS.md](../AGENTS.md) for workflow documentation
- Check [ci-integration.md](ci-integration.md) for CI setup
- See [webhook-setup.md](webhook-setup.md) for webhook configuration
- Open a PR when satisfied with changes
