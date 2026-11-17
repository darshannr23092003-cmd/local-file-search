
import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Create and return a SQLite database connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    """Create the database tables if they don't already exist."""
    connection.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            extension TEXT NOT NULL,
            size INTEGER NOT NULL,
            modified_at REAL NOT NULL,
            indexed_at REAL NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS file_contents (
            file_id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            FOREIGN KEY (file_id)
                REFERENCES files(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()


def insert_file(
    connection: sqlite3.Connection,
    path: str,
    name: str,
    extension: str,
    size: int,
    modified_at: float,
    indexed_at: float,
) -> int:
    """Insert file metadata and return its ID."""
    cursor = connection.execute(
        """
        INSERT INTO files (
            path, name, extension, size, modified_at, indexed_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (path, name, extension, size, modified_at, indexed_at),
    )

    connection.commit()

    return cursor.lastrowid


def insert_content(
    connection: sqlite3.Connection,
    file_id: int,
    content: str,
) -> None:
    """Insert extracted content associated with a file."""
    connection.execute(
        """
        INSERT INTO file_contents (file_id, content)
        VALUES (?, ?)
        """,
        (file_id, content),
    )

    connection.commit()


def get_file(
    connection: sqlite3.Connection,
    file_id: int,
) -> sqlite3.Row | None:
    """Retrieve file metadata by ID."""
    return connection.execute(
        "SELECT * FROM files WHERE id = ?",
        (file_id,),
    ).fetchone()


def get_content(
    connection: sqlite3.Connection,
    file_id: int,
) -> str | None:
    """Retrieve extracted content by file ID."""
    row = connection.execute(
        "SELECT content FROM file_contents WHERE file_id = ?",
        (file_id,),
    ).fetchone()

    return row["content"] if row else None


def delete_file(
    connection: sqlite3.Connection,
    file_id: int,
) -> None:
    """Delete file metadata and its associated content."""
    connection.execute(
        "DELETE FROM files WHERE id = ?",
        (file_id,),
    )

    connection.commit()


def update_file(
    connection: sqlite3.Connection,
    file_id: int,
    name: str,
    extension: str,
    size: int,
    modified_at: float,
    indexed_at: float,
    content: str,
) -> None:
    """
    Update file metadata and extracted content atomically.

    Raises:
        ValueError: If the file or its content record does not exist.
    """
    try:
        connection.execute("BEGIN")

        metadata_cursor = connection.execute(
            """
            UPDATE files
            SET name = ?,
                extension = ?,
                size = ?,
                modified_at = ?,
                indexed_at = ?
            WHERE id = ?
            """,
            (
                name,
                extension,
                size,
                modified_at,
                indexed_at,
                file_id,
            ),
        )

        if metadata_cursor.rowcount == 0:
            raise ValueError(f"File ID {file_id} does not exist")

        content_cursor = connection.execute(
            """
            UPDATE file_contents
            SET content = ?
            WHERE file_id = ?
            """,
            (content, file_id),
        )

        if content_cursor.rowcount == 0:
            raise ValueError(
                f"Content for file ID {file_id} does not exist"
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise
