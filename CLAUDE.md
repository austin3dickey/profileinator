# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tool Guidelines

- Package management: uv
  - Use `uv add` and `uv remove` to add/remove dependencies
  - Use `uv run` to run python commands
  - Use `uvx` to run python tools
- Testing: pytest
- Type checking: pyright
- App framework: FastAPI

## Code Style Guidelines

- Python version: 3.13+
- Formatting: Ruff formatter
- Linting: Ruff linter
- Imports: Sorted using ruff, group standard library first, then third-party, then local
- Types: Use type hints everywhere, including function returns
- Naming: snake_case for functions/variables, PascalCase for classes
- Error handling: Use specific exceptions, handle all errors appropriately
- Documentation: Docstrings for all public functions and classes
- Line length: Max 88 characters
