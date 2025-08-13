from pathlib import Path

# Resolve the project root by finding the directory containing the 'src' folder.
# This makes the path independent of where the script is run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
