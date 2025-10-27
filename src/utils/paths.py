from pathlib import Path

# Resolve the project root by finding the directory containing the 'src' folder.
# This makes the path independent of where the script is run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_data_folder(date: str) -> Path:
    """
    Get the path to the processed data folder for a given date.

    Args:
        date (str): Date string in 'YYYY-MM-DD' format (e.g., '2025-10-24')

    Returns:
        Path: Path to data/processed/MM-DD/ folder

    Example:
        >>> get_data_folder('2025-10-24')
        Path('/path/to/project/data/processed/10-24')
    """
    # Extract MM-DD from YYYY-MM-DD
    date_folder = date[5:]  # Gets 'MM-DD' from 'YYYY-MM-DD'
    return PROJECT_ROOT / "data" / "processed" / date_folder
