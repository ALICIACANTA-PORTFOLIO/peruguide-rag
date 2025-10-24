"""
Batch Embedding Processor.

This module provides efficient batch processing of texts with embedding caching,
progress tracking, and error handling for production RAG systems.

Design Principles:
- Batch processing for efficiency
- Disk caching to avoid recomputation
- Progress tracking for long operations
- Error handling and retry logic
- Memory-efficient processing
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import structlog

from src.embedding_pipeline.models.base_embedder import BaseEmbedder

logger = structlog.get_logger(__name__)


class BatchEmbeddingProcessor:
    """
    Efficient batch processor for generating and caching embeddings.
    
    This class handles:
    - Batch processing of large document sets
    - Disk-based caching to avoid recomputation
    - Progress tracking for monitoring
    - Error handling with graceful degradation
    - Memory-efficient streaming processing
    
    Cache Structure:
        cache_dir/
        ├── embeddings/
        │   ├── {hash1}.npy          # Cached embeddings
        │   ├── {hash2}.npy
        │   └── ...
        └── metadata/
            ├── {hash1}.json         # Metadata (text, model, dimension)
            ├── {hash2}.json
            └── ...
    
    Attributes:
        embedder: The embedding model instance
        cache_dir: Directory for caching embeddings
        use_cache: Whether to use caching
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
    ):
        """
        Initialize the batch embedding processor.
        
        Args:
            embedder: Embedding model instance (must implement BaseEmbedder)
            cache_dir: Directory for caching (default: data/embeddings_cache)
            use_cache: Whether to enable caching
            
        Example:
            >>> from src.embedding_pipeline.models import SentenceTransformerEmbedder
            >>> embedder = SentenceTransformerEmbedder()
            >>> processor = BatchEmbeddingProcessor(embedder)
        """
        self.embedder = embedder
        self.use_cache = use_cache
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = "data/embeddings_cache"
        
        self.cache_dir = Path(cache_dir)
        self.embeddings_dir = self.cache_dir / "embeddings"
        self.metadata_dir = self.cache_dir / "metadata"
        
        if self.use_cache:
            self.embeddings_dir.mkdir(parents=True, exist_ok=True)
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "batch_processor_initialized",
            embedder=embedder.get_model_name(),
            cache_dir=str(self.cache_dir),
            use_cache=use_cache,
        )

    def _compute_hash(self, text: str) -> str:
        """
        Compute hash for text to use as cache key.
        
        Args:
            text: Input text
            
        Returns:
            Hash string (SHA256 hex digest)
        """
        # Include model name in hash to avoid conflicts between models
        content = f"{self.embedder.get_model_name()}:{text}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _load_from_cache(self, text_hash: str) -> Optional[np.ndarray]:
        """
        Load embedding from cache if available.
        
        Args:
            text_hash: Hash of the text
            
        Returns:
            Cached embedding or None if not found
        """
        if not self.use_cache:
            return None
        
        embedding_path = self.embeddings_dir / f"{text_hash}.npy"
        
        if embedding_path.exists():
            try:
                embedding = np.load(embedding_path)
                logger.debug("cache_hit", text_hash=text_hash[:8])
                return embedding
            except Exception as e:
                logger.warning("cache_load_failed", text_hash=text_hash[:8], error=str(e))
                return None
        
        return None

    def _save_to_cache(
        self,
        text_hash: str,
        embedding: np.ndarray,
        text: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Save embedding to cache.
        
        Args:
            text_hash: Hash of the text
            embedding: Embedding vector
            text: Original text (for metadata)
            metadata: Additional metadata to store
        """
        if not self.use_cache:
            return
        
        try:
            # Save embedding
            embedding_path = self.embeddings_dir / f"{text_hash}.npy"
            np.save(embedding_path, embedding)
            
            # Save metadata
            meta_path = self.metadata_dir / f"{text_hash}.json"
            meta = {
                "text_length": len(text),
                "text_preview": text[:100] if len(text) > 100 else text,
                "model_name": self.embedder.get_model_name(),
                "dimension": self.embedder.get_dimension(),
                "shape": list(embedding.shape),
                **(metadata or {}),
            }
            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            
            logger.debug("cache_saved", text_hash=text_hash[:8])
            
        except Exception as e:
            logger.warning("cache_save_failed", text_hash=text_hash[:8], error=str(e))

    def process_single(
        self,
        text: str,
        metadata: Optional[Dict] = None,
    ) -> Tuple[np.ndarray, bool]:
        """
        Process a single text, using cache if available.
        
        Args:
            text: Input text to embed
            metadata: Optional metadata to store with cache
            
        Returns:
            Tuple of (embedding, from_cache) where from_cache is True if loaded from cache
            
        Example:
            >>> processor = BatchEmbeddingProcessor(embedder)
            >>> embedding, cached = processor.process_single("Hello world")
            >>> embedding.shape  # (768,)
            >>> cached  # False first time, True on subsequent calls
        """
        text_hash = self._compute_hash(text)
        
        # Try cache first
        cached_embedding = self._load_from_cache(text_hash)
        if cached_embedding is not None:
            return cached_embedding, True
        
        # Compute embedding
        embedding = self.embedder.encode(text)
        
        # Save to cache
        self._save_to_cache(text_hash, embedding, text, metadata)
        
        return embedding, False

    def process_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
        metadatas: Optional[List[Dict]] = None,
    ) -> Tuple[np.ndarray, Dict[str, int]]:
        """
        Process multiple texts in batches with caching.
        
        This method:
        1. Checks cache for each text
        2. Batches uncached texts for encoding
        3. Saves new embeddings to cache
        4. Returns all embeddings in original order
        
        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            show_progress: Whether to show progress
            metadatas: Optional list of metadata dicts (same length as texts)
            
        Returns:
            Tuple of (embeddings, stats) where:
                - embeddings: np.ndarray of shape (len(texts), dimension)
                - stats: dict with 'cached', 'computed', 'total' counts
                
        Example:
            >>> texts = ["Text 1", "Text 2", "Text 3"]
            >>> embeddings, stats = processor.process_batch(texts)
            >>> stats  # {'cached': 0, 'computed': 3, 'total': 3}
            >>> embeddings.shape  # (3, 768)
        """
        if not texts:
            logger.warning("process_batch_empty_input")
            return np.array([]).reshape(0, self.embedder.get_dimension()), {
                "cached": 0,
                "computed": 0,
                "total": 0,
            }
        
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError(
                f"metadatas length ({len(metadatas)}) must match texts length ({len(texts)})"
            )
        
        num_texts = len(texts)
        dimension = self.embedder.get_dimension()
        
        # Initialize result array
        embeddings = np.zeros((num_texts, dimension))
        
        # Track which texts need computation
        to_compute = []
        to_compute_indices = []
        cached_count = 0
        
        # Check cache for each text
        for i, text in enumerate(texts):
            text_hash = self._compute_hash(text)
            cached_embedding = self._load_from_cache(text_hash)
            
            if cached_embedding is not None:
                embeddings[i] = cached_embedding
                cached_count += 1
            else:
                to_compute.append(text)
                to_compute_indices.append(i)
        
        # Compute embeddings for uncached texts
        computed_count = 0
        if to_compute:
            logger.info(
                "computing_embeddings",
                total=num_texts,
                cached=cached_count,
                to_compute=len(to_compute),
            )
            
            try:
                new_embeddings = self.embedder.encode_batch(
                    to_compute,
                    batch_size=batch_size,
                    show_progress=show_progress,
                )
                
                # Place computed embeddings in result array and cache them
                for idx, original_idx in enumerate(to_compute_indices):
                    embeddings[original_idx] = new_embeddings[idx]
                    
                    # Save to cache
                    text_hash = self._compute_hash(to_compute[idx])
                    metadata = metadatas[original_idx] if metadatas else None
                    self._save_to_cache(
                        text_hash,
                        new_embeddings[idx],
                        to_compute[idx],
                        metadata,
                    )
                
                computed_count = len(to_compute)
                
            except Exception as e:
                logger.error(
                    "batch_computation_failed",
                    num_texts=len(to_compute),
                    error=str(e),
                )
                raise
        
        stats = {
            "cached": cached_count,
            "computed": computed_count,
            "total": num_texts,
        }
        
        logger.info(
            "batch_processed",
            **stats,
            cache_hit_rate=f"{cached_count/num_texts*100:.1f}%",
        )
        
        return embeddings, stats

    def clear_cache(self):
        """
        Clear all cached embeddings and metadata.
        
        Example:
            >>> processor.clear_cache()
        """
        if not self.use_cache:
            logger.warning("cache_not_enabled")
            return
        
        try:
            import shutil
            
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.embeddings_dir.mkdir(parents=True, exist_ok=True)
                self.metadata_dir.mkdir(parents=True, exist_ok=True)
                logger.info("cache_cleared", cache_dir=str(self.cache_dir))
            
        except Exception as e:
            logger.error("cache_clear_failed", error=str(e))
            raise

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
            
        Example:
            >>> stats = processor.get_cache_stats()
            >>> stats  # {'num_cached': 42, 'cache_size_mb': 15.3}
        """
        if not self.use_cache or not self.cache_dir.exists():
            return {"num_cached": 0, "cache_size_mb": 0}
        
        try:
            num_embeddings = len(list(self.embeddings_dir.glob("*.npy")))
            
            # Calculate total cache size
            total_size = sum(
                f.stat().st_size
                for f in self.cache_dir.rglob("*")
                if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            
            return {
                "num_cached": num_embeddings,
                "cache_size_mb": round(size_mb, 2),
            }
            
        except Exception as e:
            logger.warning("cache_stats_failed", error=str(e))
            return {"num_cached": 0, "cache_size_mb": 0}
