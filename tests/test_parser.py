import pytest

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
