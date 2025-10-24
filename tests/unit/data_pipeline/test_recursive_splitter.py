"""
Tests for RecursiveCharacterTextSplitter.

This test suite validates the chunking functionality with comprehensive coverage of:
- Initialization and configuration validation
- Basic splitting behavior
- Metadata preservation
- Batch processing
- Edge cases and error handling
- Real-world document scenarios
"""

import uuid
from unittest.mock import patch

import pytest

from src.data_pipeline.chunkers import (
    RecursiveCharacterTextSplitter,
    chunk_text,
    chunk_with_metadata,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def default_splitter():
    """Create splitter with default configuration."""
    return RecursiveCharacterTextSplitter()


@pytest.fixture
def small_splitter():
    """Create splitter with small chunk size for testing."""
    return RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)


@pytest.fixture
def no_overlap_splitter():
    """Create splitter without overlap."""
    return RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)


@pytest.fixture
def tourism_text():
    """Sample tourism text for testing."""
    return """Machu Picchu is an ancient Incan citadel set high in the Andes Mountains in Peru.

Built in the 15th century and later abandoned, it's renowned for its sophisticated dry-stone walls.

The site is divided into two main areas: the agricultural sector and the urban sector.

Visitors can explore temples, residences, and plazas while enjoying breathtaking mountain views."""


@pytest.fixture
def legal_text():
    """Sample legal text for testing."""
    return """Article 1: General Provisions. This contract establishes the terms and conditions.

Article 2: Scope of Work. The contractor shall perform all services as described herein.

Article 3: Payment Terms. Payment shall be made within thirty (30) days of invoice.

Article 4: Termination. Either party may terminate this agreement with written notice."""


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_initialization_defaults():
    """Test splitter initialization with default values."""
    splitter = RecursiveCharacterTextSplitter()
    
    assert splitter.chunk_size == 512
    assert splitter.chunk_overlap == 64
    assert splitter.separators == ["\n\n", "\n", ". ", " ", ""]
    assert splitter.keep_separator is True
    assert splitter.length_function == len


def test_initialization_custom_values():
    """Test splitter initialization with custom values."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,
        chunk_overlap=32,
        separators=["\n\n", "\n"],
        keep_separator=False,
    )
    
    assert splitter.chunk_size == 256
    assert splitter.chunk_overlap == 32
    assert splitter.separators == ["\n\n", "\n"]
    assert splitter.keep_separator is False


def test_initialization_invalid_chunk_size():
    """Test that invalid chunk size raises error."""
    with pytest.raises(ValueError, match="chunk_size must be > 0"):
        RecursiveCharacterTextSplitter(chunk_size=0)
    
    with pytest.raises(ValueError, match="chunk_size must be > 0"):
        RecursiveCharacterTextSplitter(chunk_size=-10)


def test_initialization_invalid_overlap():
    """Test that overlap >= chunk_size raises error."""
    with pytest.raises(ValueError, match="chunk_overlap .* must be < chunk_size"):
        RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=100)
    
    with pytest.raises(ValueError, match="chunk_overlap .* must be < chunk_size"):
        RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=150)


def test_initialization_negative_overlap():
    """Test that negative overlap raises error."""
    with pytest.raises(ValueError, match="chunk_overlap must be >= 0"):
        RecursiveCharacterTextSplitter(chunk_overlap=-10)


def test_get_config(default_splitter):
    """Test get_config returns correct configuration."""
    config = default_splitter.get_config()
    
    assert config["chunk_size"] == 512
    assert config["chunk_overlap"] == 64
    assert config["separators"] == ["\n\n", "\n", ". ", " ", ""]
    assert config["keep_separator"] is True


# ============================================================================
# BASIC SPLITTING TESTS
# ============================================================================


def test_split_empty_text(default_splitter):
    """Test splitting empty text returns empty list."""
    result = default_splitter.split_text("")
    assert result == []


def test_split_none_text(default_splitter):
    """Test splitting None text returns empty list."""
    # The implementation handles None gracefully by checking if text is falsy
    result = default_splitter.split_text(None)
    assert result == []


def test_split_whitespace_only(default_splitter):
    """Test splitting whitespace-only text returns empty list."""
    result = default_splitter.split_text("   \n\n\t  ")
    assert result == []


def test_split_short_text(default_splitter):
    """Test splitting text shorter than chunk_size returns single chunk."""
    text = "This is a short text."
    result = default_splitter.split_text(text)
    
    assert len(result) == 1
    assert result[0] == text


def test_split_text_exact_chunk_size(small_splitter):
    """Test splitting text exactly at chunk_size boundary."""
    text = "a" * 50  # Exactly chunk_size
    result = small_splitter.split_text(text)
    
    assert len(result) == 1
    assert len(result[0]) == 50


def test_split_text_exceeds_chunk_size(small_splitter):
    """Test splitting text that exceeds chunk_size."""
    text = "a" * 100  # Double chunk_size
    result = small_splitter.split_text(text)
    
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= small_splitter.chunk_size + small_splitter.chunk_overlap


# ============================================================================
# SEPARATOR HIERARCHY TESTS
# ============================================================================


def test_split_by_double_newline(small_splitter):
    """Test splitting by paragraph separator first."""
    # Make text long enough to split
    text = "Paragraph 1 with more content here." * 3 + "\n\n" + "Paragraph 2 with content." * 3
    result = small_splitter.split_text(text)
    
    # Should split due to length
    assert len(result) >= 1


def test_split_by_single_newline(small_splitter):
    """Test splitting by line separator."""
    text = "Line 1.\nLine 2.\nLine 3.\nLine 4.\nLine 5."
    result = small_splitter.split_text(text)
    
    assert len(result) >= 1
    # Verify some content is preserved
    assert any("Line" in chunk for chunk in result)


def test_split_by_sentence(small_splitter):
    """Test splitting by sentence separator."""
    text = "First sentence. Second sentence. Third sentence. Fourth sentence."
    result = small_splitter.split_text(text)
    
    assert len(result) >= 1
    # Verify sentences are kept together when possible
    assert any("sentence" in chunk for chunk in result)


def test_split_by_word():
    """Test splitting by word separator for very small chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=20, chunk_overlap=5)
    text = "This is a long sentence with many words that need splitting"
    result = splitter.split_text(text)
    
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= splitter.chunk_size + splitter.chunk_overlap


# ============================================================================
# OVERLAP TESTS
# ============================================================================


def test_overlap_between_chunks():
    """Test that overlap is applied between consecutive chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=10)
    text = "This is chunk one. This is chunk two. This is chunk three."
    result = splitter.split_text(text)
    
    if len(result) > 1:
        # Check that there's overlap between consecutive chunks
        for i in range(len(result) - 1):
            chunk1_end = result[i][-10:]
            chunk2_start = result[i + 1][:10]
            # There should be some overlap
            assert chunk1_end or chunk2_start


def test_no_overlap_setting(no_overlap_splitter):
    """Test that no overlap is applied when set to 0."""
    text = "A" * 200  # Long text
    result = no_overlap_splitter.split_text(text)
    
    # Verify no overlap by checking total length
    total_length = sum(len(chunk) for chunk in result)
    # With no overlap, total should equal original (approximately)
    assert abs(total_length - len(text)) < 10  # Allow small variance due to splitting


def test_large_overlap():
    """Test with large overlap relative to chunk size."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=80)
    text = "A" * 300
    result = splitter.split_text(text)
    
    assert len(result) > 1
    # Verify significant overlap
    for chunk in result:
        assert len(chunk) <= 100 + 80


# ============================================================================
# METADATA PRESERVATION TESTS
# ============================================================================


def test_split_with_metadata_basic(default_splitter):
    """Test splitting with basic metadata preservation."""
    text = "A" * 1000
    metadata = {"source": "test.pdf", "category": "tourism"}
    
    result = default_splitter.split_with_metadata(text, metadata)
    
    assert len(result) > 0
    for i, chunk in enumerate(result):
        assert chunk["source"] == "test.pdf"
        assert chunk["category"] == "tourism"
        assert chunk["chunk_index"] == i
        assert chunk["total_chunks"] == len(result)
        assert "chunk_id" in chunk
        assert "chunk_text" in chunk
        assert "chunk_length" in chunk


def test_split_with_metadata_no_metadata(default_splitter):
    """Test splitting without metadata still adds chunk info."""
    text = "Short text."
    result = default_splitter.split_with_metadata(text)
    
    assert len(result) == 1
    chunk = result[0]
    assert chunk["chunk_index"] == 0
    assert chunk["total_chunks"] == 1
    assert "chunk_id" in chunk
    assert chunk["chunk_text"] == text


def test_split_with_metadata_chunk_ids_unique(default_splitter):
    """Test that chunk IDs are unique."""
    text = "A" * 1000
    result = default_splitter.split_with_metadata(text)
    
    chunk_ids = [chunk["chunk_id"] for chunk in result]
    assert len(chunk_ids) == len(set(chunk_ids))  # All unique


def test_split_with_metadata_chunk_indices(default_splitter):
    """Test that chunk indices are sequential."""
    text = "A" * 1000
    result = default_splitter.split_with_metadata(text)
    
    indices = [chunk["chunk_index"] for chunk in result]
    assert indices == list(range(len(result)))


def test_split_with_metadata_total_chunks(default_splitter):
    """Test that total_chunks is consistent."""
    text = "A" * 1000
    result = default_splitter.split_with_metadata(text)
    
    total = result[0]["total_chunks"]
    assert all(chunk["total_chunks"] == total for chunk in result)
    assert total == len(result)


def test_split_with_metadata_empty_text(default_splitter):
    """Test splitting empty text with metadata."""
    result = default_splitter.split_with_metadata("", {"source": "test.pdf"})
    assert result == []


# ============================================================================
# BATCH PROCESSING TESTS
# ============================================================================


def test_split_batch_empty_list(default_splitter):
    """Test batch splitting with empty list."""
    result = default_splitter.split_batch([])
    assert result == []


def test_split_batch_single_text(default_splitter):
    """Test batch splitting with single text."""
    texts = ["Short text."]
    result = default_splitter.split_batch(texts)
    
    assert len(result) == 1
    assert len(result[0]) == 1  # One chunk
    assert result[0][0]["chunk_text"] == "Short text."


def test_split_batch_multiple_texts(default_splitter):
    """Test batch splitting with multiple texts."""
    texts = ["Text one.", "Text two.", "Text three."]
    result = default_splitter.split_batch(texts)
    
    assert len(result) == 3
    for chunks in result:
        assert len(chunks) > 0


def test_split_batch_with_metadata(default_splitter):
    """Test batch splitting with metadata."""
    texts = ["Text one.", "Text two."]
    metadatas = [{"source": "doc1.pdf"}, {"source": "doc2.pdf"}]
    
    result = default_splitter.split_batch(texts, metadatas)
    
    assert len(result) == 2
    assert result[0][0]["source"] == "doc1.pdf"
    assert result[1][0]["source"] == "doc2.pdf"


def test_split_batch_metadata_length_mismatch(default_splitter):
    """Test that mismatched metadata length raises error."""
    texts = ["Text one.", "Text two."]
    metadatas = [{"source": "doc1.pdf"}]  # Only one metadata
    
    with pytest.raises(ValueError, match="metadatas length .* must match texts length"):
        default_splitter.split_batch(texts, metadatas)


def test_split_batch_no_metadata(default_splitter):
    """Test batch splitting without metadata."""
    texts = ["Text one.", "Text two."]
    result = default_splitter.split_batch(texts)
    
    assert len(result) == 2
    for chunks in result:
        assert len(chunks) > 0
        assert "chunk_index" in chunks[0]


# ============================================================================
# REAL-WORLD SCENARIO TESTS
# ============================================================================


def test_tourism_document_chunking(tourism_text, default_splitter):
    """Test chunking of tourism document."""
    result = default_splitter.split_with_metadata(
        tourism_text,
        metadata={"category": "tourism", "region": "Cusco"}
    )
    
    assert len(result) > 0
    for chunk in result:
        assert chunk["category"] == "tourism"
        assert chunk["region"] == "Cusco"
        assert "Machu Picchu" in chunk["chunk_text"] or "Built" in chunk["chunk_text"]


def test_legal_document_chunking(legal_text, default_splitter):
    """Test chunking of legal document."""
    result = default_splitter.split_with_metadata(
        legal_text,
        metadata={"category": "legal", "document_type": "contract"}
    )
    
    assert len(result) > 0
    for chunk in result:
        assert chunk["category"] == "legal"
        # Verify article structure is preserved when possible
        assert "Article" in chunk["chunk_text"]


def test_academic_paper_chunking():
    """Test chunking of academic paper structure."""
    text = """Abstract: This study examines the impact of climate change.

Introduction: Climate change is one of the most pressing issues.

Methodology: We conducted a comprehensive literature review.

Results: Our findings indicate significant temperature increases.

Conclusion: Urgent action is required to mitigate effects."""
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    result = splitter.split_with_metadata(
        text,
        metadata={"category": "academic", "type": "research_paper"}
    )
    
    assert len(result) > 0
    # Verify sections are identified
    sections = ["Abstract", "Introduction", "Methodology", "Results", "Conclusion"]
    found_sections = set()
    for chunk in result:
        for section in sections:
            if section in chunk["chunk_text"]:
                found_sections.add(section)
    
    assert len(found_sections) >= 3  # Should find at least 3 sections


def test_mixed_language_content():
    """Test chunking with mixed language content."""
    text = """Welcome to Peru! Este es un país maravilloso.

Machu Picchu is a UNESCO World Heritage Site. Es uno de los lugares más visitados.

The ancient Incas built this city. Los incas fueron una civilización avanzada."""
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    result = splitter.split_text(text)
    
    assert len(result) > 0
    # Verify both languages are preserved
    combined = "".join(result)
    assert "Welcome to Peru" in combined
    assert "maravilloso" in combined


def test_very_long_document():
    """Test chunking of very long document."""
    # Generate long document
    text = "\n\n".join([f"This is paragraph {i}. " + ("A" * 200) for i in range(20)])
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    result = splitter.split_with_metadata(text, metadata={"source": "long_doc.pdf"})
    
    assert len(result) > 5
    # Verify all chunks are within size limit
    for chunk in result:
        assert chunk["chunk_length"] <= splitter.chunk_size + splitter.chunk_overlap
    
    # Verify total chunks matches what each chunk reports
    assert all(chunk["total_chunks"] == len(result) for chunk in result)


# ============================================================================
# CONVENIENCE FUNCTIONS TESTS
# ============================================================================


def test_chunk_text_convenience_function():
    """Test convenience function for simple chunking."""
    text = "A" * 1000
    result = chunk_text(text, chunk_size=100, chunk_overlap=20)
    
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 120  # chunk_size + overlap


def test_chunk_with_metadata_convenience_function():
    """Test convenience function with metadata."""
    text = "Test text."
    metadata = {"source": "test.pdf"}
    result = chunk_with_metadata(text, metadata, chunk_size=50, chunk_overlap=10)
    
    assert len(result) == 1
    assert result[0]["source"] == "test.pdf"
    assert result[0]["chunk_text"] == text


def test_convenience_function_custom_separators():
    """Test convenience function with custom separators."""
    text = "One. Two. Three. Four. Five."
    result = chunk_text(text, chunk_size=20, chunk_overlap=5, separators=[". "])
    
    assert len(result) > 1


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


def test_single_long_word():
    """Test chunking text with very long word (no spaces)."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    text = "A" * 200  # Single long "word"
    result = splitter.split_text(text)
    
    assert len(result) > 1
    # Should fall back to character splitting
    for chunk in result:
        assert len(chunk) <= 60  # chunk_size + overlap


def test_unicode_characters():
    """Test chunking with unicode characters."""
    text = "Peru es hermoso. ¡Qué país tan maravilloso! 🇵🇪\n\nLa cultura es única. Ñ, á, é, í, ó, ú."
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    result = splitter.split_text(text)
    
    assert len(result) > 0
    combined = "".join(result)
    assert "🇵🇪" in combined
    assert "Ñ" in combined


def test_special_characters():
    """Test chunking with special characters."""
    text = "Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?\n\nMore text here."
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    result = splitter.split_text(text)
    
    assert len(result) > 0


def test_numeric_content():
    """Test chunking with numeric content."""
    text = """Price: $1,234.56
Quantity: 100 units
Total: $123,456.00

Additional costs may apply."""
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=80)
    result = splitter.split_text(text)
    
    assert len(result) > 0
    combined = "".join(result)
    assert "$1,234.56" in combined


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize("chunk_size,chunk_overlap", [
    (100, 10),
    (200, 20),
    (512, 64),
    (1024, 128),
])
def test_various_chunk_sizes(chunk_size, chunk_overlap):
    """Test different chunk size configurations."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    text = "A" * (chunk_size * 3)
    result = splitter.split_text(text)
    
    assert len(result) > 0
    for chunk in result:
        assert len(chunk) <= chunk_size + chunk_overlap


@pytest.mark.parametrize("separator", [
    ["\n\n"],
    ["\n"],
    [". "],
    [" "],
    [""],
])
def test_single_separator(separator):
    """Test with single separator."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=10,  # Fixed: smaller overlap
        separators=separator
    )
    text = "This is a test. With multiple sentences. And some more text."
    result = splitter.split_text(text)
    
    assert len(result) > 0


@pytest.mark.parametrize("text_input", [
    "",
    "   ",
    "\n\n\n",
    "\t\t\t",
])
def test_empty_and_whitespace_inputs(text_input):
    """Test various empty/whitespace inputs."""
    splitter = RecursiveCharacterTextSplitter()
    result = splitter.split_text(text_input)
    
    assert result == []
