import pytest

from app.services import parser
from app.services.parser import get_document_type, parse_document


def test_text_document_is_decoded_without_ocr():
    content = b"Confidential information must not be disclosed."

    assert parse_document(content, "nda.txt", "text/plain") == content.decode()


@pytest.mark.parametrize(
    ("filename", "content_type", "expected"),
    [
        ("nda.pdf", "application/pdf", "pdf"),
        ("nda.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "word"),
        ("nda.md", "text/markdown", "text"),
        ("nda.unknown", "application/octet-stream", None),
    ],
)
def test_document_type_detection(filename, content_type, expected):
    assert get_document_type(b"example content", filename, content_type) == expected


def test_image_document_is_rejected():
    with pytest.raises(ValueError, match="Unsupported file type"):
        parse_document(b"example content", "scan.png", "image/png")


def test_tesseract_is_found_at_standard_windows_location(monkeypatch):
    expected_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    monkeypatch.delenv("TESSERACT_CMD", raising=False)
    monkeypatch.setenv("ProgramFiles", r"C:\Program Files")
    monkeypatch.setattr(parser.shutil, "which", lambda _: None)
    monkeypatch.setattr(
        parser.Path,
        "is_file",
        lambda path: str(path) == expected_path,
    )

    assert parser._find_tesseract_command() == expected_path


def test_configured_tesseract_path_is_preferred(monkeypatch):
    configured_path = r"D:\Tools\tesseract.exe"
    monkeypatch.setenv("TESSERACT_CMD", configured_path)
    monkeypatch.setattr(parser.os.path, "isfile", lambda path: path == configured_path)

    assert parser._find_tesseract_command() == configured_path
