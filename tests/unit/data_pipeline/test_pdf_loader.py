"""
Tests for PDF Loader module.

Following TDD principles: Test before implementation.
Goal: >80% coverage for data_pipeline module.

Test Categories:
    - Unit tests: Test individual methods
    - Integration tests: Test full loading workflow
    - Edge cases: Empty PDFs, encoding issues, missing files
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.data_pipeline.loaders.pdf_loader import (
    PDFLoader,
    Document,
    load_pdfs_from_directory
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_pdf_dir():
    """Create temporary directory for test PDFs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_content():
    """Sample PDF text content for testing."""
    return "Este es un documento de prueba sobre turismo en Perú.\nCusco es una ciudad histórica."


@pytest.fixture
def mock_pdf_reader(sample_pdf_content):
    """Mock pypdf.PdfReader for testing."""
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = sample_pdf_content
    mock_reader.pages = [mock_page]
    return mock_reader


# ============================================================================
# Unit Tests: PDFLoader Initialization
# ============================================================================

def test_pdf_loader_init_valid_directory(temp_pdf_dir):
    """Test PDFLoader initialization with valid directory."""
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    
    assert loader.source_dir == temp_pdf_dir
    assert loader.recursive is True
    assert loader.file_pattern == "*.pdf"
    assert loader.encodings == ['utf-8', 'latin-1']


def test_pdf_loader_init_custom_config(temp_pdf_dir):
    """Test PDFLoader initialization with custom configuration."""
    def custom_extractor(path, text):
        return {"custom_field": "value"}
    
    loader = PDFLoader(
        source_dir=str(temp_pdf_dir),
        recursive=False,
        file_pattern="*.PDF",
        metadata_extractor=custom_extractor,
        encodings=['utf-8']
    )
    
    assert loader.recursive is False
    assert loader.file_pattern == "*.PDF"
    assert loader.metadata_extractor is custom_extractor
    assert loader.encodings == ['utf-8']


def test_pdf_loader_init_invalid_directory():
    """Test PDFLoader initialization with non-existent directory."""
    with pytest.raises(ValueError, match="Source directory does not exist"):
        PDFLoader(source_dir="/path/that/does/not/exist")


def test_pdf_loader_init_file_not_directory(temp_pdf_dir):
    """Test PDFLoader initialization with file instead of directory."""
    # Create a file
    test_file = temp_pdf_dir / "test.txt"
    test_file.write_text("test")
    
    with pytest.raises(ValueError, match="Source path is not a directory"):
        PDFLoader(source_dir=str(test_file))


# ============================================================================
# Unit Tests: Finding PDF Files
# ============================================================================

def test_find_pdf_files_empty_directory(temp_pdf_dir):
    """Test finding PDFs in empty directory."""
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    pdf_files = loader.find_pdf_files()
    
    assert len(pdf_files) == 0


def test_find_pdf_files_multiple_pdfs(temp_pdf_dir):
    """Test finding multiple PDFs in directory."""
    # Create test PDF files
    (temp_pdf_dir / "doc1.pdf").touch()
    (temp_pdf_dir / "doc2.pdf").touch()
    (temp_pdf_dir / "doc3.PDF").touch()  # Different case
    (temp_pdf_dir / "not_pdf.txt").touch()  # Should be ignored
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    pdf_files = loader.find_pdf_files()
    
    # On Windows, *.pdf matches both .pdf and .PDF (case-insensitive)
    # On Linux/Mac, it's case-sensitive
    assert len(pdf_files) >= 2  # At least .pdf files
    assert len(pdf_files) <= 3  # Maximum if .PDF is also matched
    assert all(f.suffix.lower() == ".pdf" for f in pdf_files)


def test_find_pdf_files_recursive(temp_pdf_dir):
    """Test finding PDFs recursively in subdirectories."""
    # Create nested structure
    subdir1 = temp_pdf_dir / "subdir1"
    subdir2 = temp_pdf_dir / "subdir1" / "subdir2"
    subdir1.mkdir()
    subdir2.mkdir()
    
    (temp_pdf_dir / "root.pdf").touch()
    (subdir1 / "sub1.pdf").touch()
    (subdir2 / "sub2.pdf").touch()
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir), recursive=True)
    pdf_files = loader.find_pdf_files()
    
    assert len(pdf_files) == 3


def test_find_pdf_files_non_recursive(temp_pdf_dir):
    """Test finding PDFs only in immediate directory."""
    # Create nested structure
    subdir = temp_pdf_dir / "subdir"
    subdir.mkdir()
    
    (temp_pdf_dir / "root.pdf").touch()
    (subdir / "sub.pdf").touch()
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir), recursive=False)
    pdf_files = loader.find_pdf_files()
    
    # Should only find root.pdf
    assert len(pdf_files) == 1
    assert pdf_files[0].name == "root.pdf"


# ============================================================================
# Unit Tests: Loading Single PDF
# ============================================================================

@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_single_pdf_success(mock_reader_class, temp_pdf_dir, mock_pdf_reader, sample_pdf_content):
    """Test loading a single PDF successfully."""
    mock_reader_class.return_value = mock_pdf_reader
    
    # Create test PDF file
    pdf_path = temp_pdf_dir / "test.pdf"
    pdf_path.write_bytes(b"fake pdf content")
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    document = loader.load_single_pdf(pdf_path)
    
    assert document is not None
    assert isinstance(document, Document)
    assert document.text == sample_pdf_content
    assert document.metadata["filename"] == "test.pdf"
    assert "filepath" in document.metadata
    assert "file_size" in document.metadata


@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_single_pdf_empty_text(mock_reader_class, temp_pdf_dir):
    """Test loading PDF with empty text returns None."""
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_reader.pages = [mock_page]
    mock_reader_class.return_value = mock_reader
    
    pdf_path = temp_pdf_dir / "empty.pdf"
    pdf_path.write_bytes(b"fake pdf")
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    document = loader.load_single_pdf(pdf_path)
    
    assert document is None


@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_single_pdf_with_custom_metadata(mock_reader_class, temp_pdf_dir, mock_pdf_reader):
    """Test loading PDF with custom metadata extractor."""
    mock_reader_class.return_value = mock_pdf_reader
    
    def custom_extractor(path, text):
        return {
            "custom_field": "custom_value",
            "text_length": len(text)
        }
    
    pdf_path = temp_pdf_dir / "test.pdf"
    pdf_path.write_bytes(b"fake pdf")
    
    loader = PDFLoader(
        source_dir=str(temp_pdf_dir),
        metadata_extractor=custom_extractor
    )
    document = loader.load_single_pdf(pdf_path)
    
    assert document is not None
    assert document.metadata["custom_field"] == "custom_value"
    assert "text_length" in document.metadata


@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_single_pdf_extraction_error(mock_reader_class, temp_pdf_dir):
    """Test handling of PDF extraction errors."""
    mock_reader_class.side_effect = Exception("PDF corrupted")
    
    pdf_path = temp_pdf_dir / "corrupted.pdf"
    pdf_path.write_bytes(b"corrupted pdf")
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    document = loader.load_single_pdf(pdf_path)
    
    # Should return None on error
    assert document is None


# ============================================================================
# Unit Tests: Loading Multiple Documents
# ============================================================================

@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_documents_multiple_pdfs(mock_reader_class, temp_pdf_dir, mock_pdf_reader):
    """Test loading multiple PDF documents."""
    mock_reader_class.return_value = mock_pdf_reader
    
    # Create multiple test PDFs
    (temp_pdf_dir / "doc1.pdf").write_bytes(b"pdf1")
    (temp_pdf_dir / "doc2.pdf").write_bytes(b"pdf2")
    (temp_pdf_dir / "doc3.pdf").write_bytes(b"pdf3")
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    documents = loader.load_documents()
    
    assert len(documents) == 3
    assert all(isinstance(doc, Document) for doc in documents)


@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_documents_with_failures(mock_reader_class, temp_pdf_dir):
    """Test loading documents when some PDFs fail."""
    # Mock: first call succeeds, second fails, third succeeds
    mock_reader_success = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Valid text"
    mock_reader_success.pages = [mock_page]
    
    mock_reader_class.side_effect = [
        mock_reader_success,
        Exception("Corrupted"),
        mock_reader_success
    ]
    
    # Create test PDFs
    (temp_pdf_dir / "doc1.pdf").write_bytes(b"pdf1")
    (temp_pdf_dir / "doc2.pdf").write_bytes(b"pdf2")
    (temp_pdf_dir / "doc3.pdf").write_bytes(b"pdf3")
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    documents = loader.load_documents()
    
    # Should have loaded 2 out of 3
    assert len(documents) == 2


# ============================================================================
# Unit Tests: Document Model
# ============================================================================

def test_document_creation():
    """Test Document model creation."""
    doc = Document(
        text="Test content",
        metadata={"filename": "test.pdf"}
    )
    
    assert doc.text == "Test content"
    assert doc.metadata["filename"] == "test.pdf"
    assert doc.page_content == "Test content"  # Alias


def test_document_empty_metadata():
    """Test Document with empty metadata."""
    doc = Document(text="Test content")
    
    assert doc.text == "Test content"
    assert doc.metadata == {}


# ============================================================================
# Integration Tests
# ============================================================================

@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_load_pdfs_from_directory_utility(mock_reader_class, temp_pdf_dir, mock_pdf_reader):
    """Test utility function for loading PDFs."""
    mock_reader_class.return_value = mock_pdf_reader
    
    # Create test PDFs
    (temp_pdf_dir / "doc1.pdf").write_bytes(b"pdf1")
    (temp_pdf_dir / "doc2.pdf").write_bytes(b"pdf2")
    
    documents = load_pdfs_from_directory(str(temp_pdf_dir))
    
    assert len(documents) == 2
    assert all(isinstance(doc, Document) for doc in documents)


@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_end_to_end_loading_workflow(mock_reader_class, temp_pdf_dir):
    """Test complete end-to-end PDF loading workflow."""
    # Setup mock
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Documento sobre turismo en Cusco"
    mock_reader.pages = [mock_page]
    mock_reader_class.return_value = mock_reader
    
    # Create nested PDF structure
    subdir = temp_pdf_dir / "cusco"
    subdir.mkdir()
    
    (temp_pdf_dir / "lima.pdf").write_bytes(b"pdf1")
    (subdir / "machupicchu.pdf").write_bytes(b"pdf2")
    
    # Define custom metadata extractor
    def extract_region(path, text):
        if "cusco" in path.lower():
            return {"region": "Cusco"}
        elif "lima" in path.lower():
            return {"region": "Lima"}
        return {}
    
    # Load documents
    loader = PDFLoader(
        source_dir=str(temp_pdf_dir),
        recursive=True,
        metadata_extractor=extract_region
    )
    documents = loader.load_documents()
    
    # Assertions
    assert len(documents) == 2
    
    # Check metadata was extracted correctly
    regions = [doc.metadata.get("region") for doc in documents]
    assert "Cusco" in regions
    assert "Lima" in regions
    
    # Check all documents have required fields
    for doc in documents:
        assert "filename" in doc.metadata
        assert "filepath" in doc.metadata
        assert "file_size" in doc.metadata
        assert len(doc.text) > 0


# ============================================================================
# Edge Cases
# ============================================================================

@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_encoding_fallback(mock_reader_class, temp_pdf_dir):
    """Test encoding fallback mechanism."""
    # Mock reader to simulate encoding issues
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Texto con ñ y á"
    mock_reader.pages = [mock_page]
    mock_reader_class.return_value = mock_reader
    
    pdf_path = temp_pdf_dir / "spanish.pdf"
    pdf_path.write_bytes(b"pdf with special chars")
    
    loader = PDFLoader(
        source_dir=str(temp_pdf_dir),
        encodings=['utf-8', 'latin-1']
    )
    document = loader.load_single_pdf(pdf_path)
    
    assert document is not None
    assert "ñ" in document.text or "á" in document.text


def test_custom_metadata_extractor_error(temp_pdf_dir):
    """Test handling of custom metadata extractor errors."""
    def failing_extractor(path, text):
        raise Exception("Extractor failed")
    
    with patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader') as mock:
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test text"
        mock_reader.pages = [mock_page]
        mock.return_value = mock_reader
        
        pdf_path = temp_pdf_dir / "test.pdf"
        pdf_path.write_bytes(b"pdf")
        
        loader = PDFLoader(
            source_dir=str(temp_pdf_dir),
            metadata_extractor=failing_extractor
        )
        document = loader.load_single_pdf(pdf_path)
        
        # Should still load document with basic metadata
        assert document is not None
        assert "filename" in document.metadata


# ============================================================================
# Performance Tests (optional, for benchmarking)
# ============================================================================

@pytest.mark.slow
@patch('src.data_pipeline.loaders.pdf_loader.pypdf.PdfReader')
def test_loading_performance_many_pdfs(mock_reader_class, temp_pdf_dir, mock_pdf_reader):
    """Test loading performance with many PDFs."""
    mock_reader_class.return_value = mock_pdf_reader
    
    # Create 100 test PDFs
    for i in range(100):
        (temp_pdf_dir / f"doc{i}.pdf").write_bytes(b"pdf content")
    
    loader = PDFLoader(source_dir=str(temp_pdf_dir))
    
    import time
    start = time.time()
    documents = loader.load_documents()
    duration = time.time() - start
    
    assert len(documents) == 100
    assert duration < 10  # Should load 100 PDFs in under 10 seconds
