#!/bin/bash
set -e

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo ""
echo "Running ruff linting..."
uv run ruff check .

echo ""
echo "All checks passed!"
