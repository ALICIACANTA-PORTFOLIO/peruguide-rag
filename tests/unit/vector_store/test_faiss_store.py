"""
Tests for FaissVectorStore.

This test suite validates FAISS vector store functionality with comprehensive
coverage of add, search, delete, persist/load, and filtering operations.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from src.vector_store import FaissVectorStore


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def dimension():
    """Vector dimension for testing."""
    return 128


@pytest.fixture
def store(dimension):
    """Create a FaissVectorStore instance."""
    return FaissVectorStore(dimension=dimension)


@pytest.fixture
def sample_embeddings(dimension):
    """Generate sample embeddings."""
    np.random.seed(42)
    return np.random.randn(10, dimension).astype(np.float32)


@pytest.fixture
def sample_ids():
    """Generate sample IDs."""
    return [f"doc_{i}" for i in range(10)]


@pytest.fixture
def sample_metadatas():
    """Generate sample metadata."""
    return [{"page": i % 3, "source": f"source_{i // 3}"} for i in range(10)]


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_initialization(dimension):
    """Test store initialization."""
    store = FaissVectorStore(dimension=dimension)
    
    assert store.dimension == dimension
    assert store.index.ntotal == 0
    assert len(store.id_to_metadata) == 0
    assert store.get_dimension() == dimension


def test_initialization_creates_index(dimension):
    """Test that FAISS index is created."""
    store = FaissVectorStore(dimension=dimension)
    
    assert store.index is not None
    assert store.index.d == dimension  # FAISS dimension


def test_repr(dimension):
    """Test string representation."""
    store = FaissVectorStore(dimension=dimension)
    
    repr_str = repr(store)
    assert "FaissVectorStore" in repr_str
    assert str(dimension) in repr_str


# ============================================================================
# ADD TESTS
# ============================================================================


def test_add_vectors(store, sample_embeddings, sample_ids):
    """Test adding vectors to the store."""
    store.add(sample_embeddings, sample_ids)
    
    assert store.index.ntotal == len(sample_embeddings)
    assert len(store.id_to_index) == len(sample_ids)
    assert len(store.index_to_id) == len(sample_ids)


def test_add_with_metadata(store, sample_embeddings, sample_ids, sample_metadatas):
    """Test adding vectors with metadata."""
    store.add(sample_embeddings, sample_ids, sample_metadatas)
    
    assert len(store.id_to_metadata) == len(sample_metadatas)
    assert store.id_to_metadata["doc_0"] == sample_metadatas[0]
    assert store.id_to_metadata["doc_5"]["page"] == 5 % 3


def test_add_incremental(store, dimension):
    """Test incremental additions."""
    # First batch
    emb1 = np.random.randn(5, dimension).astype(np.float32)
    ids1 = [f"doc_{i}" for i in range(5)]
    store.add(emb1, ids1)
    
    assert store.index.ntotal == 5
    
    # Second batch
    emb2 = np.random.randn(3, dimension).astype(np.float32)
    ids2 = [f"doc_{i}" for i in range(5, 8)]
    store.add(emb2, ids2)
    
    assert store.index.ntotal == 8


def test_add_wrong_dimension(store):
    """Test adding vectors with wrong dimension."""
    wrong_emb = np.random.randn(5, 64).astype(np.float32)  # Wrong dimension
    ids = [f"doc_{i}" for i in range(5)]
    
    with pytest.raises(ValueError, match="dimension.*doesn't match"):
        store.add(wrong_emb, ids)


def test_add_mismatched_lengths(store, sample_embeddings):
    """Test adding with mismatched ID length."""
    ids = ["doc_0", "doc_1"]  # Only 2 IDs for 10 embeddings
    
    with pytest.raises(ValueError, match="Number of IDs.*doesn't match"):
        store.add(sample_embeddings, ids)


def test_add_mismatched_metadata_length(store, sample_embeddings, sample_ids):
    """Test adding with mismatched metadata length."""
    metadatas = [{"page": 1}, {"page": 2}]  # Only 2 metadatas
    
    with pytest.raises(ValueError, match="Number of metadatas.*doesn't match"):
        store.add(sample_embeddings, sample_ids, metadatas)


def test_add_duplicate_ids(store, sample_embeddings, sample_ids):
    """Test adding duplicate IDs raises error."""
    # Add first time
    store.add(sample_embeddings, sample_ids)
    
    # Try to add again with same IDs
    with pytest.raises(ValueError, match="Duplicate IDs"):
        store.add(sample_embeddings, sample_ids)


def test_add_non_2d_embeddings(store, sample_ids):
    """Test adding non-2D embeddings raises error."""
    wrong_emb = np.random.randn(128).astype(np.float32)  # 1D
    
    with pytest.raises(ValueError, match="must be 2D"):
        store.add(wrong_emb, [sample_ids[0]])


# ============================================================================
# SEARCH TESTS
# ============================================================================


def test_search_basic(store, sample_embeddings, sample_ids):
    """Test basic similarity search."""
    store.add(sample_embeddings, sample_ids)
    
    # Search with first embedding (should find itself)
    results = store.search(sample_embeddings[0], k=1)
    
    assert len(results) == 1
    assert results[0]["id"] == sample_ids[0]
    assert results[0]["score"] > 0.99  # Very similar to itself


def test_search_multiple_results(store, sample_embeddings, sample_ids):
    """Test searching for multiple results."""
    store.add(sample_embeddings, sample_ids)
    
    query = sample_embeddings[0]
    results = store.search(query, k=5)
    
    assert len(results) == 5
    assert all("id" in r for r in results)
    assert all("score" in r for r in results)
    assert all("distance" in r for r in results)
    assert all("metadata" in r for r in results)


def test_search_with_filters(store, sample_embeddings, sample_ids, sample_metadatas):
    """Test search with metadata filters."""
    store.add(sample_embeddings, sample_ids, sample_metadatas)
    
    query = sample_embeddings[0]
    
    # Filter by page=1
    results = store.search(query, k=10, filters={"page": 1})
    
    # Should only return documents with page=1
    assert all(r["metadata"]["page"] == 1 for r in results)
    assert len(results) <= 10


def test_search_empty_store(store, dimension):
    """Test searching in empty store."""
    query = np.random.randn(dimension).astype(np.float32)
    
    results = store.search(query, k=5)
    
    assert results == []


def test_search_wrong_dimension(store, sample_embeddings, sample_ids):
    """Test search with wrong dimension query."""
    store.add(sample_embeddings, sample_ids)
    
    wrong_query = np.random.randn(64).astype(np.float32)  # Wrong dimension
    
    with pytest.raises(ValueError, match="Query dimension.*doesn't match"):
        store.search(wrong_query, k=5)


def test_search_k_larger_than_store(store, sample_embeddings, sample_ids):
    """Test searching for more results than available."""
    store.add(sample_embeddings[:3], sample_ids[:3])  # Only 3 vectors
    
    query = sample_embeddings[0]
    results = store.search(query, k=10)  # Ask for 10
    
    assert len(results) == 3  # Should only return 3


def test_search_scores_ordered(store, sample_embeddings, sample_ids):
    """Test that search results are ordered by score."""
    store.add(sample_embeddings, sample_ids)
    
    query = sample_embeddings[0]
    results = store.search(query, k=5)
    
    # Scores should be in descending order
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


# ============================================================================
# DELETE TESTS
# ============================================================================


def test_delete_vectors(store, sample_embeddings, sample_ids):
    """Test deleting vectors."""
    store.add(sample_embeddings, sample_ids)
    
    initial_count = store.index.ntotal
    deleted = store.delete([sample_ids[0], sample_ids[1]])
    
    assert deleted == 2
    assert store.index.ntotal == initial_count - 2
    assert sample_ids[0] not in store.id_to_index
    assert sample_ids[1] not in store.id_to_index


def test_delete_nonexistent_ids(store, sample_embeddings, sample_ids):
    """Test deleting non-existent IDs."""
    store.add(sample_embeddings, sample_ids)
    
    deleted = store.delete(["nonexistent_1", "nonexistent_2"])
    
    assert deleted == 0
    assert store.index.ntotal == len(sample_embeddings)


def test_delete_mixed_ids(store, sample_embeddings, sample_ids):
    """Test deleting mix of existent and non-existent IDs."""
    store.add(sample_embeddings, sample_ids)
    
    deleted = store.delete([sample_ids[0], "nonexistent"])
    
    assert deleted == 1


def test_delete_all_vectors(store, sample_embeddings, sample_ids):
    """Test deleting all vectors."""
    store.add(sample_embeddings, sample_ids)
    
    deleted = store.delete(sample_ids)
    
    assert deleted == len(sample_ids)
    assert store.index.ntotal == 0
    assert len(store.id_to_index) == 0


# ============================================================================
# PERSISTENCE TESTS
# ============================================================================


def test_persist_and_load(store, sample_embeddings, sample_ids, sample_metadatas, tmp_path):
    """Test persisting and loading store."""
    # Add data
    store.add(sample_embeddings, sample_ids, sample_metadatas)
    
    # Persist
    save_path = tmp_path / "test_store"
    store.persist(str(save_path))
    
    # Check files exist
    assert (save_path / "index.faiss").exists()
    assert (save_path / "metadata.json").exists()
    
    # Load in new store
    new_store = FaissVectorStore(dimension=store.dimension)
    new_store.load(str(save_path))
    
    # Verify data
    assert new_store.index.ntotal == store.index.ntotal
    assert new_store.id_to_metadata == store.id_to_metadata
    assert new_store.id_to_index == store.id_to_index


def test_load_nonexistent_path(store, tmp_path):
    """Test loading from non-existent path."""
    with pytest.raises(FileNotFoundError, match="does not exist"):
        store.load(str(tmp_path / "nonexistent"))


def test_persist_creates_directory(store, sample_embeddings, sample_ids, tmp_path):
    """Test that persist creates directory if needed."""
    save_path = tmp_path / "nested" / "directory" / "store"
    
    store.add(sample_embeddings, sample_ids)
    store.persist(str(save_path))
    
    assert save_path.exists()
    assert (save_path / "index.faiss").exists()


def test_load_wrong_dimension(store, sample_embeddings, sample_ids, tmp_path):
    """Test loading with mismatched dimension."""
    # Create store with different dimension
    other_store = FaissVectorStore(dimension=256)
    other_embeddings = np.random.randn(5, 256).astype(np.float32)
    other_ids = [f"doc_{i}" for i in range(5)]
    other_store.add(other_embeddings, other_ids)
    
    # Persist
    save_path = tmp_path / "other_store"
    other_store.persist(str(save_path))
    
    # Try to load with different dimension
    with pytest.raises(ValueError, match="dimension.*doesn't match"):
        store.load(str(save_path))


# ============================================================================
# STATS AND UTILITY TESTS
# ============================================================================


def test_get_stats(store, sample_embeddings, sample_ids):
    """Test getting store statistics."""
    store.add(sample_embeddings, sample_ids)
    
    stats = store.get_stats()
    
    assert stats["num_vectors"] == len(sample_embeddings)
    assert stats["dimension"] == store.dimension
    assert stats["index_type"] == "IndexFlatL2"
    assert stats["memory_usage_mb"] > 0
    assert "has_metadata" in stats


def test_clear_store(store, sample_embeddings, sample_ids):
    """Test clearing the store."""
    store.add(sample_embeddings, sample_ids)
    
    assert store.index.ntotal > 0
    
    store.clear()
    
    assert store.index.ntotal == 0
    assert len(store.id_to_metadata) == 0
    assert len(store.id_to_index) == 0


def test_len(store, sample_embeddings, sample_ids):
    """Test __len__ method."""
    assert len(store) == 0
    
    store.add(sample_embeddings, sample_ids)
    
    assert len(store) == len(sample_embeddings)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_full_workflow(store, dimension, tmp_path):
    """Test complete workflow: add, search, delete, persist, load."""
    # Add vectors
    embeddings = np.random.randn(20, dimension).astype(np.float32)
    ids = [f"doc_{i}" for i in range(20)]
    metadatas = [{"category": i % 3} for i in range(20)]
    
    store.add(embeddings, ids, metadatas)
    assert store.index.ntotal == 20
    
    # Search
    query = embeddings[0]
    results = store.search(query, k=5, filters={"category": 0})
    assert len(results) > 0
    assert all(r["metadata"]["category"] == 0 for r in results)
    
    # Delete some
    deleted = store.delete(ids[:5])
    assert deleted == 5
    assert store.index.ntotal == 15
    
    # Persist
    save_path = tmp_path / "full_workflow"
    store.persist(str(save_path))
    
    # Load
    new_store = FaissVectorStore(dimension=dimension)
    new_store.load(str(save_path))
    assert new_store.index.ntotal == 15
    
    # Search in loaded store
    results = new_store.search(query, k=5)
    assert len(results) > 0


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize("num_vectors", [1, 10, 100, 500])
def test_various_vector_counts(dimension, num_vectors):
    """Test with various numbers of vectors."""
    store = FaissVectorStore(dimension=dimension)
    
    embeddings = np.random.randn(num_vectors, dimension).astype(np.float32)
    ids = [f"doc_{i}" for i in range(num_vectors)]
    
    store.add(embeddings, ids)
    
    assert store.index.ntotal == num_vectors


@pytest.mark.parametrize("k", [1, 5, 10, 20])
def test_various_k_values(store, sample_embeddings, sample_ids, k):
    """Test search with various k values."""
    store.add(sample_embeddings, sample_ids)
    
    query = sample_embeddings[0]
    results = store.search(query, k=k)
    
    expected_count = min(k, len(sample_embeddings))
    assert len(results) == expected_count
