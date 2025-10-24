"""
Semantic Retriever.

This module implements semantic retrieval by combining embedding models
with vector stores for similarity search.

Design Principles:
- Combines embedder + vector store
- Query text → embedding → similarity search
- Support for score thresholding
- Batch retrieval for efficiency
- Result formatting with metadata
"""

from typing import Any, Dict, List, Optional

import structlog

from src.embedding_pipeline.models.base_embedder import BaseEmbedder
from src.vector_store.base_store import BaseVectorStore

logger = structlog.get_logger(__name__)


class SemanticRetriever:
    """
    Semantic retriever combining embedder and vector store.
    
    This class provides semantic search functionality by:
    1. Converting text queries to embeddings
    2. Searching for similar vectors in the store
    3. Returning ranked results with metadata
    
    Features:
    - Text-to-text similarity search
    - Score thresholding
    - Metadata filtering
    - Batch query processing
    - Configurable top-k results
    
    Example:
        ```python
        # Setup
        embedder = SentenceTransformerEmbedder(dimension=768)
        vector_store = FaissVectorStore(dimension=768)
        retriever = SemanticRetriever(embedder, vector_store)
        
        # Index documents
        documents = ["Machu Picchu is...", "Cusco is...", "Lima is..."]
        doc_ids = ["doc1", "doc2", "doc3"]
        embeddings = embedder.encode_batch(documents)
        vector_store.add(embeddings, doc_ids)
        
        # Retrieve
        results = retriever.retrieve(
            query="Tell me about Machu Picchu",
            k=3,
            min_score=0.5
        )
        
        for result in results:
            print(f"ID: {result['id']}, Score: {result['score']}")
        ```
    """
    
    def __init__(
        self,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore,
    ):
        """
        Initialize semantic retriever.
        
        Args:
            embedder: Embedding model for encoding queries
            vector_store: Vector store for similarity search
            
        Raises:
            ValueError: If embedder dimension doesn't match store dimension
        """
        if embedder.get_dimension() != vector_store.get_dimension():
            raise ValueError(
                f"Embedder dimension ({embedder.get_dimension()}) doesn't match "
                f"vector store dimension ({vector_store.get_dimension()})"
            )
        
        self.embedder = embedder
        self.vector_store = vector_store
        
        logger.info(
            "retriever_initialized",
            embedder=embedder.__class__.__name__,
            vector_store=vector_store.__class__.__name__,
            dimension=embedder.get_dimension()
        )
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
        return_embeddings: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k similar documents for a query.
        
        Args:
            query: Text query to search for
            k: Number of results to return
            min_score: Minimum similarity score threshold (0-1)
            filters: Metadata filters for search
            return_embeddings: Whether to include embeddings in results
            
        Returns:
            List of result dictionaries with keys:
                - id: Document ID
                - score: Similarity score (0-1, higher is better)
                - distance: Raw L2 distance (optional, from vector store)
                - metadata: Document metadata
                - embedding: Document embedding (if return_embeddings=True)
                
        Raises:
            ValueError: If query is empty
            RuntimeError: If retrieval fails
        """
        # Validate query
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # Encode query
            logger.debug("encoding_query", query_preview=query[:50])
            query_embedding = self.embedder.encode(query)
            
            # Search in vector store
            logger.debug("searching_vector_store", k=k, filters=filters)
            results = self.vector_store.search(
                query_embedding=query_embedding,
                k=k,
                filters=filters
            )
            
            # Apply score threshold if specified
            if min_score is not None:
                original_count = len(results)
                results = [r for r in results if r["score"] >= min_score]
                filtered_count = original_count - len(results)
                
                if filtered_count > 0:
                    logger.debug(
                        "filtered_by_score",
                        filtered=filtered_count,
                        remaining=len(results),
                        min_score=min_score
                    )
            
            # Remove embeddings if not requested
            if not return_embeddings:
                for result in results:
                    result.pop("embedding", None)
            
            logger.info(
                "retrieval_completed",
                query_preview=query[:50],
                num_results=len(results),
                filters_applied=filters is not None,
                score_filtered=min_score is not None
            )
            
            return results
            
        except Exception as e:
            logger.error(
                "retrieval_failed",
                query_preview=query[:50],
                error=str(e)
            )
            raise RuntimeError(f"Retrieval failed: {e}") from e
    
    def batch_retrieve(
        self,
        queries: List[str],
        k: int = 5,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
        return_embeddings: bool = False,
    ) -> List[List[Dict[str, Any]]]:
        """
        Retrieve results for multiple queries.
        
        Args:
            queries: List of text queries
            k: Number of results per query
            min_score: Minimum similarity score threshold
            filters: Metadata filters (same for all queries)
            return_embeddings: Whether to include embeddings
            
        Returns:
            List of result lists, one per query
            
        Raises:
            ValueError: If queries list is empty
            RuntimeError: If batch retrieval fails
        """
        if not queries:
            raise ValueError("Queries list cannot be empty")
        
        logger.info("batch_retrieval_started", num_queries=len(queries))
        
        all_results = []
        for i, query in enumerate(queries):
            try:
                results = self.retrieve(
                    query=query,
                    k=k,
                    min_score=min_score,
                    filters=filters,
                    return_embeddings=return_embeddings
                )
                all_results.append(results)
                
            except Exception as e:
                logger.error(
                    "query_failed_in_batch",
                    query_index=i,
                    query_preview=query[:50],
                    error=str(e)
                )
                # Return empty results for failed query
                all_results.append([])
        
        logger.info(
            "batch_retrieval_completed",
            num_queries=len(queries),
            total_results=sum(len(r) for r in all_results)
        )
        
        return all_results
    
    def add_documents(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        batch_size: Optional[int] = None,
        show_progress: bool = False,
    ) -> None:
        """
        Add documents to the vector store.
        
        Convenience method that handles embedding and adding to store.
        
        Args:
            documents: List of document texts
            ids: List of document IDs
            metadatas: Optional metadata for each document
            batch_size: Batch size for embedding (uses embedder default if None)
            show_progress: Whether to show progress bar
            
        Raises:
            ValueError: If lengths don't match
            RuntimeError: If adding fails
        """
        if len(documents) != len(ids):
            raise ValueError(
                f"Number of documents ({len(documents)}) doesn't match "
                f"number of IDs ({len(ids)})"
            )
        
        if metadatas is not None and len(metadatas) != len(documents):
            raise ValueError(
                f"Number of metadatas ({len(metadatas)}) doesn't match "
                f"number of documents ({len(documents)})"
            )
        
        try:
            logger.info("adding_documents", num_documents=len(documents))
            
            # Encode documents
            embeddings = self.embedder.encode_batch(
                documents,
                batch_size=batch_size or 32,
                show_progress=show_progress
            )
            
            # Add to vector store
            self.vector_store.add(
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            
            logger.info(
                "documents_added",
                num_documents=len(documents),
                total_vectors=len(self.vector_store)
            )
            
        except Exception as e:
            logger.error("add_documents_failed", error=str(e))
            raise RuntimeError(f"Failed to add documents: {e}") from e
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the retriever.
        
        Returns:
            Dictionary with stats about embedder and vector store
        """
        return {
            "embedder": {
                "model_name": self.embedder.get_model_name(),
                "dimension": self.embedder.get_dimension(),
                "device": self.embedder.get_device(),
            },
            "vector_store": self.vector_store.get_stats(),
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SemanticRetriever("
            f"embedder={self.embedder.__class__.__name__}, "
            f"vector_store={self.vector_store.__class__.__name__}, "
            f"dimension={self.embedder.get_dimension()})"
        )
