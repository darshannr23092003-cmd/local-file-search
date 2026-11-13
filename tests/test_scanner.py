from local_search.scanner import scan_directory
import pytest
import local_search.scanner as scanner

def test_scanner_finds_supported_files(tmp_path): #tmp_path: pytest provides a temporary directory for each test 
    (tmp_path / "notes.txt").touch() # touch: creates an empty file
    (tmp_path / "image.png").touch()

    results = list(scan_directory(tmp_path))

    #assert len(results) == 1    #assert: verifies that the actual result matches our expectation
    assert results == [tmp_path / "notes.txt"]

def test_scanner_rejects_nonexistent_directory(tmp_path):
    invalid_path = tmp_path / "does not exist"

    with pytest.raises(FileNotFoundError):
        list(scan_directory(invalid_path))

def test_scanner_rejects_file_as_directory(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.touch()

    with pytest.raises(NotADirectoryError):
        list(scan_directory(file_path))

def test_scanner_finds_nested_files(tmp_path):
    nested_dir = tmp_path / "Projects" / "Python"
    nested_dir.mkdir(parents=True)

    file_path = nested_dir / "main.py"
    file_path.touch()

    results = list(scan_directory(tmp_path))

    assert len(results) == 1
    assert results[0].name == "main.py"

def test_scanner_handles_empty_directory(tmp_path):
    results = list(scan_directory(tmp_path))

    assert results == [] 

def test_scanner_handles_uppercase_extensions(tmp_path):
    (tmp_path / "report.PDF").touch()
    (tmp_path / "notes.TXT").touch()
    (tmp_path / "image.PNG").touch()

    results = list(scan_directory(tmp_path))

    assert len(results) == 2
    assert {file.suffix.lower() for file in results} == {".pdf", ".txt"}

def test_scanner_continues_after_permission_error(tmp_path, monkeypatch, capsys):

    def fake_walk(root, onerror):
        yield str(tmp_path), [], ["notes.txt"]

        error = PermissionError(
            13, "Permission denied", str(tmp_path / "restricted")
        )
        onerror(error)

        yield str(tmp_path), [], ["main.py"]

    monkeypatch.setattr(scanner.os, "walk", fake_walk)

    results = list(scan_directory(tmp_path))

    assert len(results) == 2
    assert {file.name for file in results} == {"notes.txt", "main.py"}

    captured = capsys.readouterr()
    assert "Permission denied" in captured.out