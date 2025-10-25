# AGENTS.md

## Commands
- **Build**: `pip install -e .`
- **Lint**: `flake8 . && black --check .`
- **Format**: `black .`
- **Test**: `pytest`
- **Single test**: `pytest tests/test_file.py::test_function_name -v`
- **Type check**: `mypy .`

## Code Style
- **Imports**: Use absolute imports, group stdlib, third-party, local imports with blank lines
- **Formatting**: Black with 88 char line length
- **Types**: Use type hints for all function parameters and return values
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Error handling**: Use specific exceptions, avoid bare except clauses
- **Docstrings**: Google style docstrings for all public functions/classes
- **Line length**: 88 characters max (Black default)

## Project Structure
- `main.py`: Entry point
- `requirements.txt`: Dependencies
- `tests/`: Test files (create if needed)