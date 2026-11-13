from pathlib import Path
from typing import Iterator
import os


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".py",
    ".java",
    ".docx",
}


def scan_directory(root: Path) -> Iterator[Path]:
    """
    Recursively discover supported files in a directory.

    Args:
        root: Directory to scan.

    Yields:
        Paths of supported files.
    """
    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    def handle_error(error: OSError) -> None:
        print(f"Could not access: {error.filename} - {error}")

    for directory, subdirectories, filenames in os.walk(
        root,
        onerror=handle_error
    ):
        for filename in filenames:
            file_path = Path(directory) / filename

            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield file_path
