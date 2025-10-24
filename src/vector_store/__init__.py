"""
Vector Store Module.

This module provides vector database implementations for similarity search
in the RAG pipeline. Uses Abstract Base Class pattern for swappable backends.

Components:
- BaseVectorStore: Abstract interface for all vector stores
- FaissVectorStore: Fast in-memory similarity search using FAISS
- (Future) ChromaVectorStore: Persistent vector database

Pattern: Abstract interface for swappable implementations
"""

from src.vector_store.base_store import BaseVectorStore
from src.vector_store.faiss_store import FaissVectorStore

__all__ = [
    "BaseVectorStore",
    "FaissVectorStore",
]
