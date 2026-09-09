from pathlib import Path

from config import DATA_DIR


PDF_DIR = Path(DATA_DIR) / "pdfs"
PDF_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def get_pdf_path(
    filename: str,
) -> Path:
    safe_name = Path(
        filename
    ).name

    return PDF_DIR / safe_name


def is_pdf(filename: str) -> bool:
    return (
        filename.lower()
        .endswith(".pdf")
    )
