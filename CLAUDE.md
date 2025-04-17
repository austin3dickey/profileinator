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
- AI model: GPT-4o

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

# This Project

This is a webapp that will use AI to generate profile pictures to use for various services, based on a picture the user uploads.

## Workflow

1. User uploads a photo on the main page.
2. This photo is sent to the AI model along with a custom prompt.
3. The AI model responds with multiple images that represent new profile pictures.
4. The page displays these choices.
5. The user can download any of these choices with buttons.

## Considerations

- No user data should be saved on the server
- If the user refreshes the page, all state is lost
- The AI model API key will be in the server's `OPENAI_API_KEY` environment variable
- The webapp should look visually pleasing but simple
- Use modern coding best practices, like modularity
- There should be unit tests and end-to-end tests with good coverage
- Code should be linted and type-checked
- Code should follow the above style guidelines
