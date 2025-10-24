"""
Retrievers Module.

This module provides semantic retrieval implementations that combine
embedding models with vector stores for similarity search.
"""

from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever

__all__ = [
    "SemanticRetriever",
]
