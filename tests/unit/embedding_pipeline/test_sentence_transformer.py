"""
Tests for SentenceTransformerEmbedder.

This test suite validates the sentence-transformers embedding functionality
with comprehensive mocking to avoid downloading models during testing.
"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
import torch

from src.embedding_pipeline.models import SentenceTransformerEmbedder


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_sentence_transformer():
    """Create a mock SentenceTransformer model."""
    mock_model = MagicMock()
    
    # Mock encode method for single text
    def mock_encode(text, **kwargs):
        if isinstance(text, str):
            # Return a single embedding (768-dim)
            return np.random.randn(768).astype(np.float32)
        else:
            # Return batch of embeddings
            return np.random.randn(len(text), 768).astype(np.float32)
    
    mock_model.encode = Mock(side_effect=mock_encode)
    
    return mock_model


@pytest.fixture
def embedder(mock_sentence_transformer):
    """Create SentenceTransformerEmbedder with mocked model."""
    with patch("sentence_transformers.SentenceTransformer") as mock_st:
        mock_st.return_value = mock_sentence_transformer
        embedder = SentenceTransformerEmbedder()
        return embedder


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_initialization_defaults():
    """Test embedder initialization with default values."""
    with patch("sentence_transformers.SentenceTransformer"):
        embedder = SentenceTransformerEmbedder()
        
        assert embedder.model_name == "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        assert embedder.dimension == 768
        assert embedder.device in ["cpu", "cuda"]
        assert embedder.normalize_embeddings is True


def test_initialization_custom_values():
    """Test embedder initialization with custom values."""
    with patch("sentence_transformers.SentenceTransformer"):
        embedder = SentenceTransformerEmbedder(
            model_name="custom-model",
            dimension=384,
            device="cpu",
            normalize_embeddings=False,
        )
        
        assert embedder.model_name == "custom-model"
        assert embedder.dimension == 384
        assert embedder.device == "cpu"
        assert embedder.normalize_embeddings is False


def test_device_auto_detection():
    """Test automatic device detection."""
    with patch("sentence_transformers.SentenceTransformer"):
        with patch("torch.cuda.is_available", return_value=True):
            embedder = SentenceTransformerEmbedder()
            assert embedder.device == "cuda"
        
        with patch("torch.cuda.is_available", return_value=False):
            embedder = SentenceTransformerEmbedder()
            assert embedder.device == "cpu"


def test_model_loaded(embedder):
    """Test that model is loaded during initialization."""
    assert embedder.model is not None


# ============================================================================
# ENCODE SINGLE TEXT TESTS
# ============================================================================


def test_encode_single_text(embedder):
    """Test encoding a single text."""
    text = "Machu Picchu es hermoso"
    embedding = embedder.encode(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (768,)
    assert embedding.dtype in [np.float32, np.float64]


def test_encode_long_text(embedder):
    """Test encoding a long text."""
    text = "This is a very long text. " * 100
    embedding = embedder.encode(text)
    
    assert embedding.shape == (768,)


def test_encode_unicode_text(embedder):
    """Test encoding text with unicode characters."""
    text = "Perú es hermoso. ¡Machu Picchu! 🇵🇪"
    embedding = embedder.encode(text)
    
    assert embedding.shape == (768,)


def test_encode_empty_text_raises_error(embedder):
    """Test that encoding empty text raises ValueError."""
    with pytest.raises(ValueError, match="Cannot encode empty"):
        embedder.encode("")


def test_encode_whitespace_only_raises_error(embedder):
    """Test that encoding whitespace-only text raises ValueError."""
    with pytest.raises(ValueError, match="Cannot encode empty"):
        embedder.encode("   \n\t  ")


# ============================================================================
# ENCODE BATCH TESTS
# ============================================================================


def test_encode_batch_multiple_texts(embedder):
    """Test encoding multiple texts."""
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = embedder.encode_batch(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (3, 768)
    assert embeddings.dtype in [np.float32, np.float64]


def test_encode_batch_empty_list(embedder):
    """Test encoding empty list returns empty array."""
    embeddings = embedder.encode_batch([])
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (0, 768)


def test_encode_batch_with_empty_texts(embedder):
    """Test encoding batch with some empty texts."""
    texts = ["Text 1", "", "Text 3", "   "]
    embeddings = embedder.encode_batch(texts)
    
    assert embeddings.shape == (4, 768)
    # Empty texts should have zero vectors
    assert np.allclose(embeddings[1], 0)
    assert np.allclose(embeddings[3], 0)


def test_encode_batch_custom_batch_size(embedder):
    """Test encoding with custom batch size."""
    texts = ["Text " + str(i) for i in range(100)]
    embeddings = embedder.encode_batch(texts, batch_size=16)
    
    assert embeddings.shape == (100, 768)


def test_encode_batch_with_progress(embedder):
    """Test encoding with progress bar enabled."""
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = embedder.encode_batch(texts, show_progress=True)
    
    assert embeddings.shape == (3, 768)


# ============================================================================
# ENCODE QUERIES/DOCUMENTS TESTS
# ============================================================================


def test_encode_queries(embedder):
    """Test encoding queries."""
    queries = ["What is Machu Picchu?", "Best time to visit Peru"]
    embeddings = embedder.encode_queries(queries)
    
    assert embeddings.shape == (2, 768)


def test_encode_documents(embedder):
    """Test encoding documents."""
    documents = ["Machu Picchu is...", "Lima is the capital..."]
    embeddings = embedder.encode_documents(documents)
    
    assert embeddings.shape == (2, 768)


# ============================================================================
# GETTER METHODS TESTS
# ============================================================================


def test_get_dimension(embedder):
    """Test get_dimension returns correct value."""
    assert embedder.get_dimension() == 768


def test_get_model_name(embedder):
    """Test get_model_name returns correct value."""
    assert "paraphrase-multilingual-mpnet-base-v2" in embedder.get_model_name()


def test_get_device(embedder):
    """Test get_device returns correct value."""
    assert embedder.get_device() in ["cpu", "cuda"]


def test_get_model_info(embedder):
    """Test get_model_info returns complete information."""
    info = embedder.get_model_info()
    
    assert "model_name" in info
    assert "dimension" in info
    assert "device" in info
    assert "normalize_embeddings" in info
    assert "cuda_available" in info
    assert "model_loaded" in info
    
    assert info["dimension"] == 768
    assert info["model_loaded"] is True


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


@pytest.mark.skip(reason="Difficult to test import error without causing recursion in mocking")
def test_import_error_when_sentence_transformers_missing():
    """Test that ImportError is raised if sentence-transformers not installed."""
    # This test would require complex import mocking that causes recursion issues.
    # In practice, if sentence-transformers is not installed, the import will fail
    # at module level with a clear error message.
    pass


def test_runtime_error_when_model_load_fails():
    """Test that RuntimeError is raised if model loading fails."""
    with patch("sentence_transformers.SentenceTransformer", side_effect=RuntimeError("Model not found")):
        with pytest.raises(RuntimeError, match="Failed to load model"):
            SentenceTransformerEmbedder()


def test_encode_runtime_error_handling(embedder):
    """Test error handling during encoding."""
    embedder.model.encode = Mock(side_effect=RuntimeError("Encoding failed"))
    
    with pytest.raises(RuntimeError, match="Failed to encode text"):
        embedder.encode("Test text")


def test_encode_batch_runtime_error_handling(embedder):
    """Test error handling during batch encoding."""
    embedder.model.encode = Mock(side_effect=RuntimeError("Batch encoding failed"))
    
    with pytest.raises(RuntimeError, match="Failed to encode batch"):
        embedder.encode_batch(["Text 1", "Text 2"])


# ============================================================================
# REPR TESTS
# ============================================================================


def test_repr(embedder):
    """Test string representation."""
    repr_str = repr(embedder)
    
    assert "SentenceTransformerEmbedder" in repr_str
    assert "model_name" in repr_str
    assert "dimension=768" in repr_str
    assert "device" in repr_str


# ============================================================================
# INTEGRATION-LIKE TESTS (with mocking)
# ============================================================================


def test_full_pipeline_simulation(embedder):
    """Test a full pipeline: encode documents and queries."""
    # Simulate document chunking
    documents = [
        "Machu Picchu is an ancient Incan citadel.",
        "Lima is the capital of Peru.",
        "Cusco was the capital of the Inca Empire.",
    ]
    
    # Encode documents
    doc_embeddings = embedder.encode_documents(documents)
    assert doc_embeddings.shape == (3, 768)
    
    # Simulate queries
    queries = [
        "What is Machu Picchu?",
        "Tell me about Peru's capital",
    ]
    
    # Encode queries
    query_embeddings = embedder.encode_queries(queries)
    assert query_embeddings.shape == (2, 768)
    
    # Verify embeddings can be used for similarity (shapes compatible)
    # In real scenario: cosine_similarity(query_embeddings, doc_embeddings)
    assert doc_embeddings.shape[1] == query_embeddings.shape[1]


def test_normalization_effect():
    """Test that normalization flag affects output."""
    with patch("sentence_transformers.SentenceTransformer") as mock_st:
        mock_model = MagicMock()
        mock_model.encode = Mock(return_value=np.random.randn(768).astype(np.float32))
        mock_st.return_value = mock_model
        
        # With normalization
        embedder_norm = SentenceTransformerEmbedder(normalize_embeddings=True)
        embedder_norm.encode("Test")
        
        # Check that normalize_embeddings was passed
        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs.get("normalize_embeddings") is True
        
        # Without normalization
        embedder_no_norm = SentenceTransformerEmbedder(normalize_embeddings=False)
        embedder_no_norm.encode("Test")
        
        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs.get("normalize_embeddings") is False


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize("text", [
    "Short text",
    "Medium length text with more words",
    "Very long text that exceeds typical sentence length. " * 10,
    "Text with números 123 y símbolos !@#$%",
])
def test_encode_various_texts(embedder, text):
    """Test encoding various text lengths and contents."""
    embedding = embedder.encode(text)
    assert embedding.shape == (768,)


@pytest.mark.parametrize("batch_size", [1, 8, 16, 32, 64])
def test_encode_batch_various_sizes(embedder, batch_size):
    """Test encoding with various batch sizes."""
    texts = ["Text " + str(i) for i in range(50)]
    embeddings = embedder.encode_batch(texts, batch_size=batch_size)
    assert embeddings.shape == (50, 768)


@pytest.mark.parametrize("num_texts", [1, 5, 10, 50, 100])
def test_encode_batch_various_counts(embedder, num_texts):
    """Test encoding various numbers of texts."""
    texts = ["Text " + str(i) for i in range(num_texts)]
    embeddings = embedder.encode_batch(texts)
    assert embeddings.shape == (num_texts, 768)

