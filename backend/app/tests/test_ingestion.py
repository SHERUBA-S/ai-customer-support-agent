import pytest
from pathlib import Path
from app.services.ingestion import ingestion_service


def test_chunking_structure():
    pages = [
        {
            "page_number": 1,
            "text": "This is a company policy statement. " * 30
        }
    ]
    chunks = ingestion_service.chunk_text(pages, "doc_test_1", "policy.txt")
    assert len(chunks) >= 1
    assert chunks[0]["document_id"] == "doc_test_1"
    assert chunks[0]["filename"] == "policy.txt"
    assert chunks[0]["page_number"] == 1
    assert "content" in chunks[0]


def test_pdf_extraction(tmp_path):
    # Verify PDF extraction on sample warranty terms
    sample_pdf = Path(__file__).resolve().parent.parent.parent / "data" / "sample_documents" / "hardware_warranty_terms.pdf"
    if sample_pdf.exists():
        pages = ingestion_service.extract_text_from_file(sample_pdf, sample_pdf.name)
        assert len(pages) == 2
        assert "WARRANTY" in pages[0]["text"].upper()


def test_unsupported_file_format():
    with pytest.raises(ValueError) as exc:
        ingestion_service.extract_text_from_file(Path("fake.exe"), "fake.exe")
    assert "Unsupported file format" in str(exc.value)
