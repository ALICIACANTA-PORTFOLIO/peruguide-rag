"""
Text Chunking Module.

This module provides domain-agnostic text chunking functionality for splitting
long documents into smaller, manageable chunks while preserving metadata.
"""

from src.data_pipeline.chunkers.recursive_splitter import (
    RecursiveCharacterTextSplitter,
    chunk_text,
    chunk_with_metadata,
)

__all__ = [
    "RecursiveCharacterTextSplitter",
    "chunk_text",
    "chunk_with_metadata",
]
