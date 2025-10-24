"""
FAISS Vector Store Implementation.

This module implements the BaseVectorStore interface using FAISS
(Facebook AI Similarity Search) for efficient similarity search.

FAISS Features:
- Fast similarity search with L2 distance
- In-memory index for quick access
- Scalable to millions of vectors
- CPU and GPU support

Design Principles:
- Implements BaseVectorStore interface
- In-memory index with disk persistence
- Metadata stored separately (FAISS only stores vectors)
- Automatic index rebuilding when needed
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import structlog

from src.vector_store.base_store import BaseVectorStore

logger = structlog.get_logger(__name__)


class FaissVectorStore(BaseVectorStore):
    """
    Vector store implementation using FAISS.
    
    This class uses FAISS IndexFlatL2 for exact L2 distance similarity search.
    Metadata is stored separately in memory and persisted alongside the index.
    
    Features:
    - Exact L2 distance search (no approximation)
    - Fast in-memory operations
    - Metadata filtering support
    - Persistence to/from disk
    - Incremental additions
    
    Example:
        ```python
        # Create store
        store = FaissVectorStore(dimension=768)
        
        # Add vectors
        embeddings = np.random.randn(100, 768).astype(np.float32)
        ids = [f"doc_{i}" for i in range(100)]
        metadatas = [{"page": i % 10} for i in range(100)]
        
        store.add(embeddings, ids, metadatas)
        
        # Search
        query = np.random.randn(768).astype(np.float32)
        results = store.search(query, k=5)
        
        # Persist
        store.persist("data/faiss_index")
        
        # Load later
        new_store = FaissVectorStore(dimension=768)
        new_store.load("data/faiss_index")
        ```
    """
    
    def __init__(self, dimension: int):
        """
        Initialize FAISS vector store.
        
        Args:
            dimension: Dimensionality of vectors (must match embeddings)
        """
        super().__init__(dimension)
        
        # Import faiss here to make it optional
        try:
            import faiss
            self.faiss = faiss
        except ImportError as e:
            logger.error("faiss_not_installed")
            raise ImportError(
                "faiss-cpu is not installed. "
                "Install with: pip install faiss-cpu"
            ) from e
        
        # Initialize FAISS index (L2 distance)
        self.index = self.faiss.IndexFlatL2(dimension)
        
        # Metadata storage (FAISS doesn't store metadata)
        self.id_to_metadata: Dict[str, Dict[str, Any]] = {}
        self.id_to_index: Dict[str, int] = {}  # Map ID to FAISS index position
        self.index_to_id: Dict[int, str] = {}  # Map FAISS index to ID
        
        logger.info(
            "faiss_store_initialized",
            dimension=dimension,
            index_type="IndexFlatL2"
        )
    
    def add(
        self,
        embeddings: np.ndarray,
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add embeddings to the FAISS index.
        
        Args:
            embeddings: Array of shape (N, dimension)
            ids: List of N unique IDs
            metadatas: Optional list of N metadata dicts
            
        Raises:
            ValueError: If shapes don't match or IDs are duplicated
        """
        # Validation
        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings must be 2D, got shape {embeddings.shape}")
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} doesn't match "
                f"store dimension {self.dimension}"
            )
        
        if len(ids) != len(embeddings):
            raise ValueError(
                f"Number of IDs ({len(ids)}) doesn't match "
                f"number of embeddings ({len(embeddings)})"
            )
        
        if metadatas is not None and len(metadatas) != len(embeddings):
            raise ValueError(
                f"Number of metadatas ({len(metadatas)}) doesn't match "
                f"number of embeddings ({len(embeddings)})"
            )
        
        # Check for duplicate IDs
        duplicate_ids = set(ids) & set(self.id_to_index.keys())
        if duplicate_ids:
            logger.warning(
                "duplicate_ids_found",
                num_duplicates=len(duplicate_ids),
                examples=list(duplicate_ids)[:5]
            )
            raise ValueError(f"Duplicate IDs found: {list(duplicate_ids)[:5]}")
        
        # Ensure float32 (FAISS requirement)
        embeddings = embeddings.astype(np.float32)
        
        # Add to FAISS index
        start_index = self.index.ntotal
        self.index.add(embeddings)
        
        # Store metadata mappings
        for i, doc_id in enumerate(ids):
            faiss_index = start_index + i
            self.id_to_index[doc_id] = faiss_index
            self.index_to_id[faiss_index] = doc_id
            
            if metadatas is not None:
                self.id_to_metadata[doc_id] = metadatas[i]
            else:
                self.id_to_metadata[doc_id] = {}
        
        logger.info(
            "vectors_added",
            num_vectors=len(ids),
            total_vectors=self.index.ntotal
        )
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for k most similar vectors using L2 distance.
        
        Lower L2 distance = more similar (0 = identical).
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            k: Number of results
            filters: Metadata filters (applied post-search)
            
        Returns:
            List of result dictionaries sorted by similarity (best first)
        """
        # Validation
        if query_embedding.shape[0] != self.dimension:
            raise ValueError(
                f"Query dimension {query_embedding.shape[0]} doesn't match "
                f"store dimension {self.dimension}"
            )
        
        if self.index.ntotal == 0:
            logger.warning("search_on_empty_index")
            return []
        
        # Reshape to (1, dimension) and ensure float32
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search in FAISS (returns L2 distances)
        # We might need more results if filtering
        search_k = min(k * 10 if filters else k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, search_k)
        
        # Convert to results
        results = []
        for i in range(len(indices[0])):
            faiss_idx = int(indices[0][i])
            distance = float(distances[0][i])
            
            # Get ID and metadata
            doc_id = self.index_to_id.get(faiss_idx)
            if doc_id is None:
                logger.warning("missing_id_for_index", faiss_index=faiss_idx)
                continue
            
            metadata = self.id_to_metadata.get(doc_id, {})
            
            # Apply filters if provided
            if filters:
                if not self._matches_filters(metadata, filters):
                    continue
            
            # Convert L2 distance to similarity score (inverse)
            # Lower distance = higher score
            # score = 1 / (1 + distance)
            score = 1.0 / (1.0 + distance)
            
            results.append({
                "id": doc_id,
                "score": score,
                "distance": distance,  # Include raw distance
                "metadata": metadata.copy()
            })
            
            # Stop if we have enough results
            if len(results) >= k:
                break
        
        logger.info(
            "search_completed",
            k_requested=k,
            k_returned=len(results),
            filters_applied=filters is not None
        )
        
        return results
    
    def delete(self, ids: List[str]) -> int:
        """
        Delete vectors by ID.
        
        Note: FAISS doesn't support efficient deletion, so we rebuild the index.
        This can be slow for large indices.
        
        Args:
            ids: List of IDs to delete
            
        Returns:
            Number of vectors deleted
        """
        # Find IDs that exist
        existing_ids = [doc_id for doc_id in ids if doc_id in self.id_to_index]
        
        if not existing_ids:
            logger.info("delete_no_matching_ids", requested=len(ids))
            return 0
        
        # Get all current vectors except the ones to delete
        remaining_ids = [
            doc_id for doc_id in self.id_to_index.keys()
            if doc_id not in existing_ids
        ]
        
        if not remaining_ids:
            # Deleting everything - just clear
            self.clear()
            return len(existing_ids)
        
        # Rebuild index with remaining vectors
        remaining_indices = [self.id_to_index[doc_id] for doc_id in remaining_ids]
        remaining_embeddings = np.vstack([
            self.index.reconstruct(int(idx)) for idx in remaining_indices
        ])
        remaining_metadatas = [
            self.id_to_metadata[doc_id] for doc_id in remaining_ids
        ]
        
        # Clear and rebuild
        self.clear()
        self.add(remaining_embeddings, remaining_ids, remaining_metadatas)
        
        logger.info(
            "vectors_deleted",
            num_deleted=len(existing_ids),
            num_remaining=len(remaining_ids)
        )
        
        return len(existing_ids)
    
    def persist(self, path: str) -> None:
        """
        Save index and metadata to disk.
        
        Creates directory with:
        - index.faiss: FAISS index
        - metadata.json: ID mappings and metadata
        """
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = path_obj / "index.faiss"
        self.faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_dict = {
            "dimension": self.dimension,
            "num_vectors": self.index.ntotal,
            "id_to_metadata": self.id_to_metadata,
            "id_to_index": self.id_to_index,
            "index_to_id": {str(k): v for k, v in self.index_to_id.items()},
        }
        
        metadata_path = path_obj / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(
            "store_persisted",
            path=str(path_obj),
            num_vectors=self.index.ntotal
        )
    
    def load(self, path: str) -> None:
        """
        Load index and metadata from disk.
        
        Args:
            path: Directory containing index.faiss and metadata.json
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        # Load FAISS index
        index_path = path_obj / "index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        self.index = self.faiss.read_index(str(index_path))
        
        # Load metadata
        metadata_path = path_obj / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata_dict = json.load(f)
        
        # Validate dimension
        if metadata_dict["dimension"] != self.dimension:
            raise ValueError(
                f"Loaded dimension {metadata_dict['dimension']} doesn't match "
                f"store dimension {self.dimension}"
            )
        
        # Restore metadata
        self.id_to_metadata = metadata_dict["id_to_metadata"]
        self.id_to_index = metadata_dict["id_to_index"]
        self.index_to_id = {int(k): v for k, v in metadata_dict["index_to_id"].items()}
        
        logger.info(
            "store_loaded",
            path=str(path_obj),
            num_vectors=self.index.ntotal
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the FAISS store."""
        return {
            "num_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": "IndexFlatL2",
            "memory_usage_mb": self._estimate_memory_usage(),
            "has_metadata": len(self.id_to_metadata) > 0,
        }
    
    def clear(self) -> None:
        """Remove all vectors and metadata."""
        self.index.reset()
        self.id_to_metadata.clear()
        self.id_to_index.clear()
        self.index_to_id.clear()
        
        logger.info("store_cleared")
    
    # Helper methods
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches all filters."""
        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        # FAISS index: num_vectors * dimension * 4 bytes (float32)
        index_size = self.index.ntotal * self.dimension * 4
        
        # Metadata: rough estimate
        metadata_size = len(json.dumps(self.id_to_metadata).encode())
        
        total_bytes = index_size + metadata_size
        return total_bytes / (1024 * 1024)  # Convert to MB
