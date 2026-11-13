from pathlib import Path
from pypdf import PdfReader

SUPPORTED_TEXT_EXTENSIONS = {
    ".txt",
    ".py",
    ".java",
}


def extract_text(file_path: Path) -> str:
    """
    Extract text from supported UTF-8 text files.

    Raises:
        ValueError: If the file extension is unsupported.
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the file is not valid UTF-8.
    """
    if file_path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    with file_path.open("r", encoding="utf-8") as file:
        return file.read()

def extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages)