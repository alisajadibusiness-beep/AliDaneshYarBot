from pathlib import Path

from config import DATA_DIR


FILES_DIR = Path(DATA_DIR) / "files"

FILES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def safe_filename(
    filename: str,
) -> str:
    return Path(filename).name


def save_path(
    filename: str,
) -> Path:
    return FILES_DIR / safe_filename(
        filename
    )
