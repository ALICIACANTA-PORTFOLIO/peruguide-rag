"""
Retrieval Pipeline Module.

This module handles semantic document retrieval by combining embedding models
with vector stores for similarity search.

Components:
- SemanticRetriever: Combines embedder + vector store for semantic search
- (Future) HybridRetriever: Combines dense + sparse retrieval
- (Future) Rerankers: Cross-encoder reranking for precision
"""

from src.retrieval_pipeline.retrievers import SemanticRetriever

__all__ = [
    "SemanticRetriever",
]
