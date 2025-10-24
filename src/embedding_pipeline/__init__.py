"""
Embedding Pipeline Module

Generates vector embeddings for text chunks using sentence-transformers.

Components:
    - models: Embedding model wrappers (BaseEmbedder, SentenceTransformerEmbedder)
    - batch_processor: Batch processing with caching for efficiency

Model: paraphrase-multilingual-mpnet-base-v2 (768-dim)
Justification: Hands-On LLMs p.145 - "Multilingual transformers excel at cross-lingual search"
"""

from src.embedding_pipeline.batch_processor import BatchEmbeddingProcessor
from src.embedding_pipeline.models import (
    BaseEmbedder,
    SentenceTransformerEmbedder,
)

__all__ = [
    "BaseEmbedder",
    "SentenceTransformerEmbedder",
    "BatchEmbeddingProcessor",
]
