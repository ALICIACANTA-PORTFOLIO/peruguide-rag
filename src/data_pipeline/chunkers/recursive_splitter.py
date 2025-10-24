"""
Text Chunking Module - Recursive Character Text Splitter.

This module provides domain-agnostic text chunking functionality using a recursive
splitting strategy with configurable separators and overlap.

Design Principles:
- Domain-agnostic: Works with any text content (tourism, legal, academic, etc.)
- Metadata preservation: All document metadata flows through to chunks
- Configurable: Chunk size, overlap, and separators from settings
- Performance: Efficient batch processing
- Testable: Clean interfaces with dependency injection

Example:
    >>> from src.data_pipeline.chunkers import RecursiveCharacterTextSplitter
    >>> 
    >>> splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    >>> chunks = splitter.split_text("Your long text here...")
    >>> print(f"Created {len(chunks)} chunks")
    >>> 
    >>> # With metadata preservation
    >>> metadata = {"source": "document.pdf", "category": "tourism"}
    >>> chunk_with_metadata = splitter.split_with_metadata(
    ...     text="Long text...",
    ...     metadata=metadata
    ... )
"""

import re
import uuid
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class RecursiveCharacterTextSplitter:
    """
    Recursively split text using a hierarchy of separators.
    
    This splitter attempts to keep semantically related text together by trying
    separators in order (e.g., paragraphs, then sentences, then words, then characters).
    
    Algorithm:
    1. Try to split by first separator (e.g., r"\\n\\n" for paragraphs)
    2. If chunks are still too large, try next separator (e.g., r"\\n" for lines)
    3. Continue recursively until all chunks are within size limit
    4. Apply overlap between consecutive chunks for context preservation
    
    Attributes:
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of overlapping characters between chunks
        separators: List of regex patterns to try splitting on, in order of preference
        length_function: Function to measure text length (default: len)
        keep_separator: Whether to keep separator in chunks (default: True)
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        separators: Optional[List[str]] = None,
        length_function: callable = len,
        keep_separator: bool = True,
    ):
        """
        Initialize the recursive character text splitter.
        
        Args:
            chunk_size: Maximum characters per chunk (must be > 0)
            chunk_overlap: Characters to overlap between chunks (must be < chunk_size)
            separators: List of separator patterns (default: [r"\\n\\n", r"\\n", r"\\. ", r" ", r""])
            length_function: Function to measure text length
            keep_separator: Whether to keep separators in output
            
        Raises:
            ValueError: If chunk_size <= 0 or chunk_overlap >= chunk_size
        """
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be < chunk_size ({chunk_size})")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be >= 0, got {chunk_overlap}")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self.length_function = length_function
        self.keep_separator = keep_separator

        logger.info(
            "recursive_splitter_initialized",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            num_separators=len(self.separators),
        )

    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks using recursive splitting strategy.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks, each <= chunk_size with overlap applied
            
        Example:
            >>> splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
            >>> text = "First paragraph.\\n\\nSecond paragraph.\\n\\nThird paragraph."
            >>> chunks = splitter.split_text(text)
            >>> len(chunks)  # Returns number of chunks
        """
        if not text or not text.strip():
            logger.debug("split_text_empty_input")
            return []

        chunks = self._split_text_recursive(text, self.separators)
        chunks = self._merge_splits(chunks, self.chunk_size, self.chunk_overlap)

        logger.info(
            "split_text_completed",
            input_length=len(text),
            num_chunks=len(chunks),
            avg_chunk_size=sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
        )

        return chunks

    def split_with_metadata(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text and preserve metadata in each chunk.
        
        Each chunk receives:
        - All original document metadata
        - chunk_index: Position in sequence (0-based)
        - total_chunks: Total number of chunks
        - chunk_id: Unique identifier for this chunk
        - chunk_text: The actual text content
        
        Args:
            text: Input text to split
            metadata: Original document metadata to preserve
            
        Returns:
            List of dictionaries with text and metadata
            
        Example:
            >>> splitter = RecursiveCharacterTextSplitter(chunk_size=100)
            >>> metadata = {"source": "doc.pdf", "category": "tourism"}
            >>> results = splitter.split_with_metadata("Long text...", metadata)
            >>> results[0]["chunk_index"]  # 0
            >>> results[0]["source"]  # "doc.pdf"
        """
        chunks = self.split_text(text)
        metadata = metadata or {}
        total_chunks = len(chunks)

        results = []
        for idx, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "chunk_id": str(uuid.uuid4()),
                "chunk_text": chunk_text,
                "chunk_length": len(chunk_text),
            }
            results.append(chunk_metadata)

        logger.info(
            "split_with_metadata_completed",
            num_chunks=total_chunks,
            metadata_keys=list(metadata.keys()),
        )

        return results

    def split_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        Split multiple texts in batch, preserving metadata.
        
        Args:
            texts: List of input texts to split
            metadatas: Optional list of metadata dicts (must match texts length)
            
        Returns:
            List of chunk lists, one per input text
            
        Raises:
            ValueError: If metadatas provided but length doesn't match texts
            
        Example:
            >>> splitter = RecursiveCharacterTextSplitter()
            >>> texts = ["Text 1...", "Text 2..."]
            >>> metadatas = [{"source": "doc1.pdf"}, {"source": "doc2.pdf"}]
            >>> results = splitter.split_batch(texts, metadatas)
            >>> len(results)  # 2 (one per input text)
        """
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError(f"metadatas length ({len(metadatas)}) must match texts length ({len(texts)})")

        if metadatas is None:
            metadatas = [{}] * len(texts)

        results = []
        for text, metadata in zip(texts, metadatas):
            chunks = self.split_with_metadata(text, metadata)
            results.append(chunks)

        total_chunks = sum(len(chunks) for chunks in results)
        logger.info(
            "split_batch_completed",
            num_documents=len(texts),
            total_chunks=total_chunks,
            avg_chunks_per_doc=total_chunks / len(texts) if texts else 0,
        )

        return results

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using separator hierarchy.
        
        Args:
            text: Text to split
            separators: List of separators to try, in order
            
        Returns:
            List of text segments
        """
        if not separators:
            # Base case: no more separators, return text as-is
            return [text] if text else []

        separator = separators[0]
        remaining_separators = separators[1:]

        # Split by current separator
        if separator:
            splits = re.split(f"({re.escape(separator)})", text)
        else:
            # Empty separator means split into characters
            splits = list(text)

        # Filter out empty strings
        splits = [s for s in splits if s]

        # Merge splits with separator if keep_separator is True
        if self.keep_separator and separator:
            merged_splits = []
            for i in range(0, len(splits), 2):
                if i + 1 < len(splits):
                    merged_splits.append(splits[i] + splits[i + 1])
                else:
                    merged_splits.append(splits[i])
            splits = merged_splits

        # Check if any split is too large
        final_splits = []
        for split in splits:
            if self.length_function(split) <= self.chunk_size:
                final_splits.append(split)
            else:
                # Recursively split large segments with next separator
                sub_splits = self._split_text_recursive(split, remaining_separators)
                final_splits.extend(sub_splits)

        return final_splits

    def _merge_splits(
        self,
        splits: List[str],
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """
        Merge small splits into chunks with overlap.
        
        This function combines small splits to approach chunk_size while
        maintaining overlap between consecutive chunks.
        
        Args:
            splits: List of text segments to merge
            chunk_size: Target chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of merged chunks
        """
        if not splits:
            return []

        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = self.length_function(split)

            # If adding this split would exceed chunk_size, finalize current chunk
            if current_length + split_length > chunk_size and current_chunk:
                chunk_text = "".join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_text = chunk_text[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = [overlap_text, split] if overlap_text else [split]
                current_length = len(overlap_text) + split_length
            else:
                current_chunk.append(split)
                current_length += split_length

        # Add final chunk if any
        if current_chunk:
            chunks.append("".join(current_chunk))

        return chunks

    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.
        
        Returns:
            Dictionary with chunk_size, chunk_overlap, and separators
            
        Example:
            >>> splitter = RecursiveCharacterTextSplitter(chunk_size=256)
            >>> config = splitter.get_config()
            >>> config["chunk_size"]  # 256
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "separators": self.separators,
            "keep_separator": self.keep_separator,
        }


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    separators: Optional[List[str]] = None,
) -> List[str]:
    """
    Convenience function to chunk text with default settings.
    
    Args:
        text: Input text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks
        separators: List of separator patterns
        
    Returns:
        List of text chunks
        
    Example:
        >>> from src.data_pipeline.chunkers import chunk_text
        >>> chunks = chunk_text("Your long text here...", chunk_size=100)
        >>> print(f"Created {len(chunks)} chunks")
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    return splitter.split_text(text)


def chunk_with_metadata(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    separators: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk text with metadata preservation.
    
    Args:
        text: Input text to split
        metadata: Document metadata to preserve
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks
        separators: List of separator patterns
        
    Returns:
        List of chunks with metadata
        
    Example:
        >>> from src.data_pipeline.chunkers import chunk_with_metadata
        >>> metadata = {"source": "document.pdf", "category": "tourism"}
        >>> chunks = chunk_with_metadata("Long text...", metadata)
        >>> chunks[0]["chunk_index"]  # 0
        >>> chunks[0]["category"]  # "tourism"
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    return splitter.split_with_metadata(text, metadata)
