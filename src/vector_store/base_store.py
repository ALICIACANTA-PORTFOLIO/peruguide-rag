"""
Base Vector Store Interface.

This module defines the abstract base class for all vector store implementations,
ensuring a consistent interface across different vector database backends.

Design Principles:
- Abstract Base Class (ABC) pattern for polymorphism
- Consistent interface for add, search, delete operations
- Support for metadata filtering
- Persistence and loading capabilities
- Type hints for clarity
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class BaseVectorStore(ABC):
    """
    Abstract base class for vector store implementations.
    
    This class defines the interface that all vector store implementations
    must follow, enabling easy switching between different backends
    (FAISS, ChromaDB, Pinecone, etc.) without changing application code.
    
    Key Operations:
    - Add embeddings with IDs and metadata
    - Search for similar vectors
    - Delete vectors by ID
    - Persist and load from disk
    - Get statistics about the store
    
    Example:
        ```python
        # Using a concrete implementation
        store = FaissVectorStore(dimension=768)
        
        # Add vectors
        store.add(
            embeddings=embeddings,
            ids=["doc1", "doc2", "doc3"],
            metadatas=[{"page": 1}, {"page": 2}, {"page": 3}]
        )
        
        # Search
        results = store.search(
            query_embedding=query_vec,
            k=5,
            filters={"page": 1}
        )
        
        # Persist
        store.persist("path/to/index")
        ```
    """
    
    def __init__(self, dimension: int):
        """
        Initialize vector store.
        
        Args:
            dimension: Dimensionality of the vectors (e.g., 768 for sentence-transformers)
        """
        self.dimension = dimension
    
    @abstractmethod
    def add(
        self,
        embeddings: np.ndarray,
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add embeddings to the vector store.
        
        Args:
            embeddings: Array of shape (N, dimension) containing embeddings
            ids: List of N unique string identifiers for each embedding
            metadatas: Optional list of N metadata dictionaries
            
        Raises:
            ValueError: If embeddings shape doesn't match dimension
            ValueError: If lengths of embeddings, ids, and metadatas don't match
            RuntimeError: If adding vectors fails
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for k most similar vectors.
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            k: Number of results to return
            filters: Optional metadata filters (e.g., {"page": 1, "source": "book"})
            
        Returns:
            List of k dictionaries with keys:
                - id: str - Vector ID
                - score: float - Similarity score (higher = more similar)
                - metadata: dict - Associated metadata
                - embedding: np.ndarray - The vector (optional, for inspection)
                
        Raises:
            ValueError: If query_embedding shape doesn't match dimension
            RuntimeError: If search fails
        """
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> int:
        """
        Delete vectors by their IDs.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            Number of vectors actually deleted
            
        Raises:
            RuntimeError: If deletion fails
        """
        pass
    
    @abstractmethod
    def persist(self, path: str) -> None:
        """
        Save the vector store to disk.
        
        Args:
            path: Directory path where to save the store
            
        Raises:
            RuntimeError: If persistence fails
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """
        Load the vector store from disk.
        
        Args:
            path: Directory path from where to load the store
            
        Raises:
            FileNotFoundError: If path doesn't exist
            RuntimeError: If loading fails
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with stats like:
                - num_vectors: int - Total number of vectors
                - dimension: int - Vector dimensionality
                - index_type: str - Type of index used
                - memory_usage_mb: float - Approximate memory usage
                
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Remove all vectors from the store.
        
        Raises:
            RuntimeError: If clearing fails
        """
        pass
    
    # Concrete methods (shared across implementations)
    
    def get_dimension(self) -> int:
        """Get the vector dimension."""
        return self.dimension
    
    def __repr__(self) -> str:
        """String representation of the vector store."""
        return f"{self.__class__.__name__}(dimension={self.dimension})"
    
    def __len__(self) -> int:
        """
        Get number of vectors in the store.
        
        Subclasses should override this to provide efficient implementation.
        """
        stats = self.get_stats()
        return stats.get("num_vectors", 0)
