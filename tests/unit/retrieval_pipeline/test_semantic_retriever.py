"""
Tests for SemanticRetriever.

This test suite validates the semantic retriever functionality including
query encoding, similarity search, filtering, and batch operations.
"""

from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

from src.retrieval_pipeline import SemanticRetriever


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def dimension():
    """Vector dimension for testing."""
    return 128


@pytest.fixture
def mock_embedder(dimension):
    """Create a mock embedder."""
    embedder = MagicMock()
    embedder.get_dimension.return_value = dimension
    embedder.get_model_name.return_value = "mock-embedder"
    embedder.get_device.return_value = "cpu"
    
    # Mock encode to return deterministic embeddings
    def mock_encode(text, **kwargs):
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(dimension).astype(np.float32)
    
    # Mock encode_batch
    def mock_encode_batch(texts, **kwargs):
        return np.array([mock_encode(t) for t in texts])
    
    embedder.encode = Mock(side_effect=mock_encode)
    embedder.encode_batch = Mock(side_effect=mock_encode_batch)
    
    return embedder


@pytest.fixture
def mock_vector_store(dimension):
    """Create a mock vector store."""
    store = MagicMock()
    store.get_dimension.return_value = dimension
    store.__len__.return_value = 10
    
    # Mock search to return results
    def mock_search(query_embedding, k=5, filters=None):
        results = []
        for i in range(min(k, 10)):
            results.append({
                "id": f"doc_{i}",
                "score": 1.0 / (i + 1),  # Decreasing scores
                "distance": float(i),
                "metadata": {"page": i % 3, "source": "test"}
            })
        
        # Apply filters if provided
        if filters:
            results = [r for r in results if all(
                r["metadata"].get(k) == v for k, v in filters.items()
            )]
        
        return results
    
    store.search = Mock(side_effect=mock_search)
    store.add = Mock()
    store.get_stats = Mock(return_value={
        "num_vectors": 10,
        "dimension": dimension
    })
    
    return store


@pytest.fixture
def retriever(mock_embedder, mock_vector_store):
    """Create a SemanticRetriever instance."""
    return SemanticRetriever(mock_embedder, mock_vector_store)


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_initialization(mock_embedder, mock_vector_store):
    """Test retriever initialization."""
    retriever = SemanticRetriever(mock_embedder, mock_vector_store)
    
    assert retriever.embedder == mock_embedder
    assert retriever.vector_store == mock_vector_store


def test_initialization_dimension_mismatch():
    """Test initialization with mismatched dimensions."""
    embedder = MagicMock()
    embedder.get_dimension.return_value = 128
    
    store = MagicMock()
    store.get_dimension.return_value = 256  # Different!
    
    with pytest.raises(ValueError, match="dimension.*doesn't match"):
        SemanticRetriever(embedder, store)


def test_repr(retriever):
    """Test string representation."""
    repr_str = repr(retriever)
    
    assert "SemanticRetriever" in repr_str
    assert "dimension=" in repr_str


# ============================================================================
# RETRIEVE TESTS
# ============================================================================


def test_retrieve_basic(retriever, mock_embedder, mock_vector_store):
    """Test basic retrieval."""
    query = "What is Machu Picchu?"
    results = retriever.retrieve(query, k=3)
    
    # Check embedder was called
    mock_embedder.encode.assert_called_once_with(query)
    
    # Check vector store was called
    mock_vector_store.search.assert_called_once()
    
    # Check results
    assert len(results) == 3
    assert all("id" in r for r in results)
    assert all("score" in r for r in results)


def test_retrieve_with_filters(retriever, mock_vector_store):
    """Test retrieval with metadata filters."""
    query = "test query"
    filters = {"page": 1}
    
    results = retriever.retrieve(query, k=5, filters=filters)
    
    # Check filters were passed to vector store
    call_kwargs = mock_vector_store.search.call_args[1]
    assert call_kwargs["filters"] == filters
    
    # Check all results match filter
    assert all(r["metadata"]["page"] == 1 for r in results)


def test_retrieve_with_min_score(retriever):
    """Test retrieval with score threshold."""
    query = "test query"
    
    # Without threshold
    results_all = retriever.retrieve(query, k=10)
    
    # With threshold
    results_filtered = retriever.retrieve(query, k=10, min_score=0.5)
    
    # Should have fewer results
    assert len(results_filtered) <= len(results_all)
    
    # All remaining should be above threshold
    assert all(r["score"] >= 0.5 for r in results_filtered)


def test_retrieve_empty_query(retriever):
    """Test retrieval with empty query."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("")
    
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("   ")


def test_retrieve_no_embeddings_in_results(retriever):
    """Test that embeddings are not included by default."""
    query = "test query"
    results = retriever.retrieve(query, k=3, return_embeddings=False)
    
    assert all("embedding" not in r for r in results)


def test_retrieve_with_embeddings(retriever, mock_vector_store):
    """Test retrieval with embeddings included."""
    # Add embedding to mock results
    def mock_search_with_emb(query_embedding, k=5, filters=None):
        return [{
            "id": "doc_0",
            "score": 1.0,
            "distance": 0.0,
            "metadata": {},
            "embedding": np.random.randn(128).astype(np.float32)
        }]
    
    mock_vector_store.search = Mock(side_effect=mock_search_with_emb)
    
    query = "test query"
    results = retriever.retrieve(query, k=1, return_embeddings=True)
    
    assert "embedding" in results[0]


def test_retrieve_handles_encoder_error(retriever, mock_embedder):
    """Test retrieval handles encoding errors."""
    mock_embedder.encode.side_effect = RuntimeError("Encoding failed")
    
    with pytest.raises(RuntimeError, match="Retrieval failed"):
        retriever.retrieve("test query")


# ============================================================================
# BATCH RETRIEVE TESTS
# ============================================================================


def test_batch_retrieve_basic(retriever, mock_embedder):
    """Test batch retrieval."""
    queries = ["query 1", "query 2", "query 3"]
    results = retriever.batch_retrieve(queries, k=3)
    
    # Should return list of lists
    assert len(results) == len(queries)
    assert all(isinstance(r, list) for r in results)
    
    # Embedder should be called for each query
    assert mock_embedder.encode.call_count == len(queries)


def test_batch_retrieve_empty_queries(retriever):
    """Test batch retrieval with empty list."""
    with pytest.raises(ValueError, match="Queries list cannot be empty"):
        retriever.batch_retrieve([])


def test_batch_retrieve_with_filters(retriever, mock_vector_store):
    """Test batch retrieval with filters."""
    queries = ["query 1", "query 2"]
    filters = {"source": "test"}
    
    results = retriever.batch_retrieve(queries, k=3, filters=filters)
    
    # Filters should be applied to all queries
    assert mock_vector_store.search.call_count == len(queries)


def test_batch_retrieve_handles_query_failure(retriever, mock_embedder):
    """Test batch retrieval handles individual query failures."""
    # Make second query fail
    call_count = [0]
    original_encode = mock_embedder.encode.side_effect
    
    def encode_with_failure(text, **kwargs):
        call_count[0] += 1
        if call_count[0] == 2:
            raise RuntimeError("Encoding failed")
        return original_encode(text, **kwargs)
    
    mock_embedder.encode.side_effect = encode_with_failure
    
    queries = ["query 1", "query 2", "query 3"]
    results = retriever.batch_retrieve(queries, k=3)
    
    # Should return 3 results (second one empty)
    assert len(results) == 3
    assert len(results[0]) > 0  # First succeeded
    assert len(results[1]) == 0  # Second failed
    assert len(results[2]) > 0  # Third succeeded


# ============================================================================
# ADD DOCUMENTS TESTS
# ============================================================================


def test_add_documents_basic(retriever, mock_embedder, mock_vector_store):
    """Test adding documents."""
    documents = ["Doc 1", "Doc 2", "Doc 3"]
    ids = ["id1", "id2", "id3"]
    
    retriever.add_documents(documents, ids)
    
    # Embedder should encode batch
    mock_embedder.encode_batch.assert_called_once()
    
    # Vector store should add
    mock_vector_store.add.assert_called_once()


def test_add_documents_with_metadata(retriever, mock_embedder, mock_vector_store):
    """Test adding documents with metadata."""
    documents = ["Doc 1", "Doc 2"]
    ids = ["id1", "id2"]
    metadatas = [{"page": 1}, {"page": 2}]
    
    retriever.add_documents(documents, ids, metadatas)
    
    # Check metadata was passed
    call_kwargs = mock_vector_store.add.call_args[1]
    assert call_kwargs["metadatas"] == metadatas


def test_add_documents_mismatched_lengths(retriever):
    """Test adding documents with mismatched lengths."""
    documents = ["Doc 1", "Doc 2"]
    ids = ["id1"]  # Wrong length
    
    with pytest.raises(ValueError, match="Number of documents.*doesn't match"):
        retriever.add_documents(documents, ids)


def test_add_documents_mismatched_metadata_length(retriever):
    """Test adding with mismatched metadata length."""
    documents = ["Doc 1", "Doc 2"]
    ids = ["id1", "id2"]
    metadatas = [{"page": 1}]  # Wrong length
    
    with pytest.raises(ValueError, match="Number of metadatas.*doesn't match"):
        retriever.add_documents(documents, ids, metadatas)


def test_add_documents_with_batch_size(retriever, mock_embedder):
    """Test adding documents with custom batch size."""
    documents = ["Doc 1", "Doc 2", "Doc 3"]
    ids = ["id1", "id2", "id3"]
    
    retriever.add_documents(documents, ids, batch_size=16)
    
    # Check batch_size was passed to encode_batch
    call_kwargs = mock_embedder.encode_batch.call_args[1]
    assert call_kwargs["batch_size"] == 16


def test_add_documents_handles_error(retriever, mock_embedder):
    """Test add_documents handles errors."""
    mock_embedder.encode_batch.side_effect = RuntimeError("Encoding failed")
    
    with pytest.raises(RuntimeError, match="Failed to add documents"):
        retriever.add_documents(["Doc 1"], ["id1"])


# ============================================================================
# UTILITY TESTS
# ============================================================================


def test_get_stats(retriever, mock_embedder, mock_vector_store):
    """Test getting retriever stats."""
    stats = retriever.get_stats()
    
    assert "embedder" in stats
    assert "vector_store" in stats
    
    assert stats["embedder"]["model_name"] == "mock-embedder"
    assert stats["embedder"]["dimension"] == 128
    assert stats["embedder"]["device"] == "cpu"
    
    assert stats["vector_store"]["num_vectors"] == 10


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_full_workflow(retriever, dimension):
    """Test complete workflow: add documents and retrieve."""
    # Add documents
    documents = [
        "Machu Picchu is an ancient Incan city",
        "Cusco was the capital of the Inca Empire",
        "Lima is the capital of Peru"
    ]
    ids = ["doc1", "doc2", "doc3"]
    metadatas = [
        {"topic": "machu_picchu"},
        {"topic": "cusco"},
        {"topic": "lima"}
    ]
    
    retriever.add_documents(documents, ids, metadatas)
    
    # Retrieve
    results = retriever.retrieve(
        query="Tell me about Machu Picchu",
        k=2,
        min_score=0.0
    )
    
    assert len(results) <= 2
    assert all("id" in r for r in results)
    assert all("score" in r for r in results)
    assert all("metadata" in r for r in results)


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize("k", [1, 3, 5, 10])
def test_various_k_values(retriever, k):
    """Test retrieval with various k values."""
    results = retriever.retrieve("test query", k=k)
    
    # Should return at most k results (or less if not enough in store)
    assert len(results) <= k


@pytest.mark.parametrize("min_score", [0.0, 0.3, 0.5, 0.8])
def test_various_min_scores(retriever, min_score):
    """Test retrieval with various minimum scores."""
    results = retriever.retrieve("test query", k=10, min_score=min_score)
    
    # All results should be above threshold
    assert all(r["score"] >= min_score for r in results)


@pytest.mark.parametrize("num_queries", [1, 3, 5, 10])
def test_batch_various_sizes(retriever, num_queries):
    """Test batch retrieval with various batch sizes."""
    queries = [f"query {i}" for i in range(num_queries)]
    results = retriever.batch_retrieve(queries, k=3)
    
    assert len(results) == num_queries
