from pathlib import Path
from local_search.extractor import extract_text, extract_pdf_text
import pytest
from pypdf import PdfWriter
from reportlab.pdfgen import canvas
from docx import Document

def test_extract_text_from_txt(tmp_path):
    # Arrange: create a sample text file
    file_path = tmp_path / "sample.txt"
    expected_content = "Hello, local search engine!"

    file_path.write_text(expected_content, encoding="utf-8")

    # Act: extract its contents
    actual_content = extract_text(file_path)

    # Assert: compare actual and expected content
    assert actual_content == expected_content

def test_extract_text_from_empty_txt(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.touch()

    result = extract_text(file_path)

    assert result == ""

def test_extract_text_from_missing_file(tmp_path):
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        extract_text(file_path)

def test_extract_text_with_invalid_encoding(tmp_path):
    file_path = tmp_path / "invalid.txt"
    file_path.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(UnicodeDecodeError):
        extract_text(file_path)

def test_extract_text_from_python_file(tmp_path):
    file_path = tmp_path / "sample.py"
    expected_content = "print('Hello World')"

    file_path.write_text(expected_content, encoding="utf-8")

    actual_content = extract_text(file_path)

    assert actual_content == expected_content

def test_extract_text_from_java_file(tmp_path):
    file_path = tmp_path / "Main.java"
    expected_content = 'public class Main { public static void main(String[] args) {} }'

    file_path.write_text(expected_content, encoding="utf-8")

    actual_content = extract_text(file_path)

    assert actual_content == expected_content

def test_extract_text_from_unsupported_file(tmp_path):
    file_path = tmp_path / "image.png"
    file_path.write_bytes(b"fake image data")

    with pytest.raises(ValueError):
        extract_text(file_path)

def test_extract_text_from_pdf(tmp_path):
    file_path = tmp_path / "sample.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    with file_path.open("wb") as file:
        writer.write(file)

    result = extract_pdf_text(file_path)

    assert result == ""

def test_extract_text_from_pdf_with_content(tmp_path):
    file_path = tmp_path / "sample_with_text.pdf"

    pdf = canvas.Canvas(str(file_path))
    pdf.drawString(100, 750, "Hello PDF")
    pdf.save()

    result = extract_pdf_text(file_path)

    assert "Hello PDF" in result

def test_extract_text_from_docx(tmp_path):
    file_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("Hello DOCX")
    document.add_paragraph("Local search engine")
    document.save(file_path)

    result = extract_text(file_path)

    assert "Hello DOCX" in result
    assert "Local search engine" in result

def test_extract_text_from_empty_docx(tmp_path):
    file_path = tmp_path / "empty.docx"

    document = Document()
    document.save(file_path)

    result = extract_text(file_path)

    assert result == ""