"""
PeruGuide AI - Production-Ready RAG System

A professional RAG (Retrieval-Augmented Generation) system for Peru tourism information,
built following best practices from authoritative ML/AI engineering resources.

Modules:
    - data_pipeline: Data ingestion, processing, and chunking
    - embedding_pipeline: Embedding generation and batch processing
    - vector_store: Vector database management (FAISS/Chroma)
    - retrieval_pipeline: Document retrieval and reranking
    - inference_pipeline: LLM inference and RAG orchestration
    - evaluation: RAGAS evaluation and metrics
    - utils: Common utilities (logging, monitoring)

Based on research from:
    - LLM Engineer's Handbook (Iusztin & Labonne)
    - Hands-On Large Language Models (Alammar & Grootendorst)
    - Build a Large Language Model from Scratch (Raschka)
    - + 6 more authoritative sources (2,959 pages analyzed)

Version: 0.1.0
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import key components for easy access
# TODO: Uncomment as modules are implemented
# from src.config import settings
# from src.data_pipeline import PDFLoader
# from src.embedding_pipeline import EmbeddingModel
# from src.vector_store import VectorStore
# from src.inference_pipeline import RAGChain

__all__ = [
    "__version__",
    "__author__",
    "__email__",
]
