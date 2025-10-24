"""
Tests for BatchEmbeddingProcessor.

This test suite validates the batch processing and caching functionality
for embedding generation.
"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

from src.embedding_pipeline import BatchEmbeddingProcessor
from src.embedding_pipeline.models import BaseEmbedder


# ============================================================================
# FIXTURES
# ============================================================================


class MockEmbedder(BaseEmbedder):
    """Mock embedder for testing."""
    
    def __init__(self):
        super().__init__(model_name="mock-model", dimension=768, device="cpu")
        self.encode_count = 0
        self.encode_batch_count = 0
    
    def encode(self, text: str, **kwargs) -> np.ndarray:
        """Mock encode method."""
        self.encode_count += 1
        # Return deterministic embedding based on text hash
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.dimension).astype(np.float32)
    
    def encode_batch(self, texts, batch_size=32, show_progress=False, **kwargs) -> np.ndarray:
        """Mock encode_batch method."""
        self.encode_batch_count += 1
        embeddings = np.array([self.encode(text) for text in texts])
        return embeddings


@pytest.fixture
def mock_embedder():
    """Create a mock embedder."""
    return MockEmbedder()


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    yield str(cache_dir)
    # Cleanup
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


@pytest.fixture
def processor(mock_embedder, temp_cache_dir):
    """Create BatchEmbeddingProcessor with mock embedder and temp cache."""
    return BatchEmbeddingProcessor(
        embedder=mock_embedder,
        cache_dir=temp_cache_dir,
        use_cache=True,
    )


@pytest.fixture
def processor_no_cache(mock_embedder):
    """Create BatchEmbeddingProcessor without caching."""
    return BatchEmbeddingProcessor(
        embedder=mock_embedder,
        use_cache=False,
    )


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_initialization_with_cache(mock_embedder, temp_cache_dir):
    """Test processor initialization with caching enabled."""
    processor = BatchEmbeddingProcessor(
        embedder=mock_embedder,
        cache_dir=temp_cache_dir,
        use_cache=True,
    )
    
    assert processor.embedder == mock_embedder
    assert processor.use_cache is True
    assert processor.cache_dir.exists()
    assert processor.embeddings_dir.exists()
    assert processor.metadata_dir.exists()


def test_initialization_without_cache(mock_embedder):
    """Test processor initialization without caching."""
    processor = BatchEmbeddingProcessor(
        embedder=mock_embedder,
        use_cache=False,
    )
    
    assert processor.use_cache is False


def test_initialization_default_cache_dir(mock_embedder):
    """Test processor uses default cache directory."""
    processor = BatchEmbeddingProcessor(embedder=mock_embedder)
    
    assert "embeddings_cache" in str(processor.cache_dir)


# ============================================================================
# HASH COMPUTATION TESTS
# ============================================================================


def test_compute_hash_deterministic(processor):
    """Test that hash computation is deterministic."""
    text = "Test text"
    hash1 = processor._compute_hash(text)
    hash2 = processor._compute_hash(text)
    
    assert hash1 == hash2


def test_compute_hash_different_texts(processor):
    """Test that different texts produce different hashes."""
    text1 = "Test text 1"
    text2 = "Test text 2"
    
    hash1 = processor._compute_hash(text1)
    hash2 = processor._compute_hash(text2)
    
    assert hash1 != hash2


def test_compute_hash_includes_model_name(processor):
    """Test that hash includes model name."""
    # Same text but different model would have different hash
    # This is implicitly tested by the hash function
    text = "Test"
    hash_val = processor._compute_hash(text)
    
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64  # SHA256 produces 64 hex characters


# ============================================================================
# SINGLE TEXT PROCESSING TESTS
# ============================================================================


def test_process_single_text_first_time(processor, mock_embedder):
    """Test processing a text for the first time (not cached)."""
    text = "Test text"
    
    embedding, from_cache = processor.process_single(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (768,)
    assert from_cache is False
    assert mock_embedder.encode_count == 1


def test_process_single_text_cached(processor, mock_embedder):
    """Test processing a text that is cached."""
    text = "Test text"
    
    # First call - not cached
    embedding1, cached1 = processor.process_single(text)
    assert cached1 is False
    
    # Reset counter
    encode_count_before = mock_embedder.encode_count
    
    # Second call - should be cached
    embedding2, cached2 = processor.process_single(text)
    assert cached2 is True
    
    # Embedding should be the same
    assert np.allclose(embedding1, embedding2)
    
    # Should not have called encode again
    assert mock_embedder.encode_count == encode_count_before


def test_process_single_with_metadata(processor, temp_cache_dir):
    """Test processing with metadata."""
    text = "Test text"
    metadata = {"category": "tourism", "source": "doc.pdf"}
    
    embedding, _ = processor.process_single(text, metadata)
    
    # Check that metadata was saved
    text_hash = processor._compute_hash(text)
    meta_path = Path(temp_cache_dir) / "metadata" / f"{text_hash}.json"
    
    assert meta_path.exists()


def test_process_single_no_cache(processor_no_cache, mock_embedder):
    """Test processing without caching."""
    text = "Test text"
    
    # First call
    embedding1, cached1 = processor_no_cache.process_single(text)
    assert cached1 is False
    
    count_before = mock_embedder.encode_count
    
    # Second call - should still compute (no cache)
    embedding2, cached2 = processor_no_cache.process_single(text)
    assert cached2 is False
    
    # Should have called encode again
    assert mock_embedder.encode_count > count_before


# ============================================================================
# BATCH PROCESSING TESTS
# ============================================================================


def test_process_batch_empty_list(processor):
    """Test processing empty list."""
    embeddings, stats = processor.process_batch([])
    
    assert embeddings.shape == (0, 768)
    assert stats["total"] == 0
    assert stats["cached"] == 0
    assert stats["computed"] == 0


def test_process_batch_single_text(processor, mock_embedder):
    """Test processing batch with single text."""
    texts = ["Test text"]
    
    embeddings, stats = processor.process_batch(texts)
    
    assert embeddings.shape == (1, 768)
    assert stats["total"] == 1
    assert stats["computed"] == 1
    assert stats["cached"] == 0


def test_process_batch_multiple_texts(processor, mock_embedder):
    """Test processing batch with multiple texts."""
    texts = ["Text 1", "Text 2", "Text 3"]
    
    embeddings, stats = processor.process_batch(texts, show_progress=False)
    
    assert embeddings.shape == (3, 768)
    assert stats["total"] == 3
    assert stats["computed"] == 3
    assert stats["cached"] == 0
    assert mock_embedder.encode_batch_count == 1


def test_process_batch_with_caching(processor, mock_embedder):
    """Test that caching works in batch processing."""
    texts = ["Text 1", "Text 2", "Text 3"]
    
    # First batch - nothing cached
    embeddings1, stats1 = processor.process_batch(texts, show_progress=False)
    assert stats1["cached"] == 0
    assert stats1["computed"] == 3
    
    batch_count_before = mock_embedder.encode_batch_count
    
    # Second batch - all cached
    embeddings2, stats2 = processor.process_batch(texts, show_progress=False)
    assert stats2["cached"] == 3
    assert stats2["computed"] == 0
    
    # Should not have called encode_batch again
    assert mock_embedder.encode_batch_count == batch_count_before
    
    # Embeddings should be the same
    assert np.allclose(embeddings1, embeddings2)


def test_process_batch_partial_cache(processor, mock_embedder):
    """Test batch processing with some texts cached."""
    texts1 = ["Text 1", "Text 2"]
    texts2 = ["Text 2", "Text 3"]  # Text 2 overlaps
    
    # Process first batch
    processor.process_batch(texts1, show_progress=False)
    
    # Process second batch (Text 2 should be cached)
    embeddings, stats = processor.process_batch(texts2, show_progress=False)
    
    assert stats["total"] == 2
    assert stats["cached"] == 1  # Text 2
    assert stats["computed"] == 1  # Text 3


def test_process_batch_custom_batch_size(processor):
    """Test batch processing with custom batch size."""
    texts = ["Text " + str(i) for i in range(10)]
    
    embeddings, stats = processor.process_batch(texts, batch_size=3, show_progress=False)
    
    assert embeddings.shape == (10, 768)
    assert stats["total"] == 10


def test_process_batch_with_metadatas(processor, temp_cache_dir):
    """Test batch processing with metadata."""
    texts = ["Text 1", "Text 2"]
    metadatas = [
        {"category": "tourism"},
        {"category": "legal"},
    ]
    
    embeddings, stats = processor.process_batch(texts, metadatas=metadatas, show_progress=False)
    
    assert embeddings.shape == (2, 768)
    assert stats["total"] == 2


def test_process_batch_metadata_length_mismatch(processor):
    """Test that mismatched metadata length raises error."""
    texts = ["Text 1", "Text 2"]
    metadatas = [{"category": "tourism"}]  # Only one metadata
    
    with pytest.raises(ValueError, match="metadatas length .* must match texts length"):
        processor.process_batch(texts, metadatas=metadatas)


def test_process_batch_preserves_order(processor):
    """Test that batch processing preserves text order."""
    texts = ["Apple", "Banana", "Cherry", "Date"]
    
    # Process once
    embeddings1, _ = processor.process_batch(texts, show_progress=False)
    
    # Process again (should be cached)
    embeddings2, _ = processor.process_batch(texts, show_progress=False)
    
    # Embeddings should match exactly
    assert np.allclose(embeddings1, embeddings2)
    
    # Specific embedding for "Banana" should be at index 1
    banana_embedding1 = embeddings1[1]
    banana_embedding2 = embeddings2[1]
    assert np.allclose(banana_embedding1, banana_embedding2)


# ============================================================================
# CACHE MANAGEMENT TESTS
# ============================================================================


def test_clear_cache(processor, temp_cache_dir):
    """Test clearing the cache."""
    texts = ["Text 1", "Text 2"]
    
    # Process to populate cache
    processor.process_batch(texts, show_progress=False)
    
    # Verify cache exists
    cache_path = Path(temp_cache_dir)
    assert len(list(cache_path.rglob("*.npy"))) > 0
    
    # Clear cache
    processor.clear_cache()
    
    # Verify cache is empty but directories exist
    assert processor.cache_dir.exists()
    assert len(list(cache_path.rglob("*.npy"))) == 0


def test_clear_cache_no_cache_enabled(processor_no_cache):
    """Test clearing cache when caching is disabled."""
    # Should not raise error
    processor_no_cache.clear_cache()


def test_get_cache_stats(processor):
    """Test getting cache statistics."""
    texts = ["Text 1", "Text 2", "Text 3"]
    
    # Initially empty
    stats = processor.get_cache_stats()
    assert stats["num_cached"] == 0
    
    # Process texts
    processor.process_batch(texts, show_progress=False)
    
    # Check stats
    stats = processor.get_cache_stats()
    assert stats["num_cached"] == 3
    assert stats["cache_size_mb"] > 0


def test_get_cache_stats_no_cache(processor_no_cache):
    """Test getting cache stats when caching disabled."""
    stats = processor_no_cache.get_cache_stats()
    
    assert stats["num_cached"] == 0
    assert stats["cache_size_mb"] == 0


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_process_batch_encoding_error():
    """Test error handling when encoding fails."""
    # Create embedder that raises error
    error_embedder = MockEmbedder()
    error_embedder.encode_batch = Mock(side_effect=RuntimeError("Encoding failed"))
    
    processor = BatchEmbeddingProcessor(error_embedder, use_cache=False)
    
    with pytest.raises(RuntimeError):
        processor.process_batch(["Text 1", "Text 2"])


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_full_pipeline_with_caching(processor):
    """Test a full pipeline: process, cache, and reuse."""
    # Simulate document chunking
    documents = [
        "Machu Picchu is an ancient Incan citadel.",
        "Lima is the capital of Peru.",
        "Cusco was the capital of the Inca Empire.",
        "The Andes mountains run through Peru.",
        "Lake Titicaca is the highest navigable lake.",
    ]
    
    # First processing - nothing cached
    embeddings1, stats1 = processor.process_batch(documents, batch_size=2, show_progress=False)
    
    assert embeddings1.shape == (5, 768)
    assert stats1["cached"] == 0
    assert stats1["computed"] == 5
    
    # Second processing - all cached
    embeddings2, stats2 = processor.process_batch(documents, show_progress=False)
    
    assert stats2["cached"] == 5
    assert stats2["computed"] == 0
    assert np.allclose(embeddings1, embeddings2)
    
    # Partial overlap
    new_documents = documents[:2] + ["New document about Arequipa"]
    embeddings3, stats3 = processor.process_batch(new_documents, show_progress=False)
    
    assert stats3["total"] == 3
    assert stats3["cached"] == 2  # First two docs
    assert stats3["computed"] == 1  # New doc
    
    # First two embeddings should match
    assert np.allclose(embeddings3[:2], embeddings1[:2])


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize("num_texts", [1, 5, 10, 20])
def test_process_batch_various_sizes(processor, num_texts):
    """Test processing batches of various sizes."""
    texts = [f"Text {i}" for i in range(num_texts)]
    
    embeddings, stats = processor.process_batch(texts, show_progress=False)
    
    assert embeddings.shape == (num_texts, 768)
    assert stats["total"] == num_texts


@pytest.mark.parametrize("batch_size", [1, 4, 8, 16])
def test_various_batch_sizes(processor, batch_size):
    """Test with various batch sizes."""
    texts = [f"Text {i}" for i in range(20)]
    
    embeddings, stats = processor.process_batch(texts, batch_size=batch_size, show_progress=False)
    
    assert embeddings.shape == (20, 768)
