#!/bin/bash
# This script sets up the Python environment and Jupyter kernel for the McCell project.

set -e # Exit immediately if a command fails.

echo "--- Syncing Python environment with uv ---"
# This creates the .venv and installs all packages from the lock file.
uv sync

echo ""
echo "--- Creating Jupyter kernel for the environment ---"
# This registers the .venv as a kernel named 'mccell'.
uv run python -m ipykernel install --user --name=mccell --display-name="McCell"

echo ""
echo "--- Verifying kernel installation ---"
uv run jupyter kernelspec list

echo ""
echo "Setup complete. You can now select the 'McCell' kernel in Jupyter."
