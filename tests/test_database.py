import sqlite3
import pytest

from local_search.database import (
    get_connection,
    create_tables,
    insert_file,
    insert_content,
    get_file,
    get_content,
    delete_file,
    update_file,
)

def test_get_connection_creates_database(tmp_path):
    db_path = tmp_path / "data" / "test.db"

    connection = get_connection(db_path)

    assert db_path.exists()
    assert isinstance(connection, sqlite3.Connection)

    connection.close()

def test_create_tables(tmp_path):
    connection = get_connection(tmp_path / "test.db")

    create_tables(connection)

    cursor = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    tables = {row["name"] for row in cursor.fetchall()}

    assert "files" in tables
    assert "file_contents" in tables

    connection.close()

def test_insert_and_get_file(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    file_id = insert_file(
        connection,
        path="C:/docs/example.txt",
        name="example.txt",
        extension=".txt",
        size=100,
        modified_at=1000.0,
        indexed_at=1100.0,
    )

    result = get_file(connection, file_id)

    assert result["name"] == "example.txt"
    assert result["extension"] == ".txt"
    assert result["size"] == 100

    connection.close()

def test_insert_and_get_content(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    file_id = insert_file(
        connection,
        path="C:/docs/example.txt",
        name="example.txt",
        extension=".txt",
        size=100,
        modified_at=1000.0,
        indexed_at=1100.0,
    )

    insert_content(connection, file_id, "Hello local search engine")

    result = get_content(connection, file_id)

    assert result == "Hello local search engine"

    connection.close()

def test_duplicate_file_path_raises_error(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    insert_file(
        connection,
        "C:/docs/example.txt",
        "example.txt",
        ".txt",
        100,
        1000.0,
        1100.0,
    )

    with pytest.raises(sqlite3.IntegrityError):
        insert_file(
            connection,
            "C:/docs/example.txt",
            "example.txt",
            ".txt",
            100,
            1000.0,
            1100.0,
        )

    connection.close()

def test_content_requires_existing_file(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    with pytest.raises(sqlite3.IntegrityError):
        insert_content(connection, 999, "Some content")

    connection.close()

def test_delete_file_cascades_to_content(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    file_id = insert_file(
        connection,
        "C:/docs/example.txt",
        "example.txt",
        ".txt",
        100,
        1000.0,
        1100.0,
    )

    insert_content(connection, file_id, "Hello world")

    delete_file(connection, file_id)

    assert get_file(connection, file_id) is None
    assert get_content(connection, file_id) is None

    connection.close()

def test_get_nonexistent_file_returns_none(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    assert get_file(connection, 999) is None
    assert get_content(connection, 999) is None

    connection.close()

def test_delete_nonexistent_file_does_not_raise_error(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    delete_file(connection, 999)

    assert get_file(connection, 999) is None

    connection.close()

def test_update_file_updates_metadata_and_content(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    file_id = insert_file(
        connection,
        "C:/docs/example.txt",
        "example.txt",
        ".txt",
        100,
        1000.0,
        1100.0,
    )
    insert_content(connection, file_id, "Old content")

    update_file(
        connection,
        file_id,
        "updated.txt",
        ".txt",
        200,
        1200.0,
        1300.0,
        "New content",
    )

    result = get_file(connection, file_id)

    assert result["name"] == "updated.txt"
    assert result["size"] == 200
    assert get_content(connection, file_id) == "New content"

    connection.close()

def test_update_nonexistent_file_raises_error(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    with pytest.raises(ValueError):
        update_file(
            connection, 999, "missing.txt", ".txt",
            100, 1000.0, 1100.0, "Content"
        )

    connection.close()

def test_update_file_rolls_back_when_content_missing(tmp_path):
    connection = get_connection(tmp_path / "test.db")
    create_tables(connection)

    file_id = insert_file(
        connection,
        "C:/docs/example.txt",
        "example.txt",
        ".txt",
        100,
        1000.0,
        1100.0,
    )

    with pytest.raises(ValueError):
        update_file(
            connection,
            file_id,
            "updated.txt",
            ".txt",
            200,
            1200.0,
            1300.0,
            "New content",
        )

    result = get_file(connection, file_id)

    assert result["name"] == "example.txt"
    assert result["size"] == 100

    connection.close()