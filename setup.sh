#!/bin/bash
# Setup script for Profileinator

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "uv package manager is required but not installed."
    echo "Please install it from https://github.com/astral-sh/uv"
    exit 1
fi

# Install the application and development dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]"

# Check for OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set."
    echo "You will need to set it before running the application:"
    echo "export OPENAI_API_KEY=your-api-key-here"
fi

echo "Setup complete! You can now run the application with:"
echo "uv run profileinator"