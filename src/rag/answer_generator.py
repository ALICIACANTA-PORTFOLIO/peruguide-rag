"""Answer Generator for RAG Pipeline."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional

import structlog

from src.llm.base_llm import BaseLLM, Message, StreamChunk
from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever

log = structlog.get_logger()


@dataclass
class RetrievalResult:
    """Result from semantic retrieval."""
    
    content: str
    """Document content/text"""
    
    score: float
    """Similarity score (0-1, higher is better)"""
    
    doc_id: Optional[str] = None
    """Document identifier"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Document metadata"""


@dataclass
class RAGResponse:
    """Response from RAG generation with sources."""
    
    answer: str
    """Generated answer text"""
    
    sources: List[Dict[str, Any]]
    """List of source documents used (with metadata and scores)"""
    
    query: str
    """Original user query"""
    
    model: str
    """LLM model used for generation"""
    
    usage: Optional[Dict[str, int]] = None
    """Token usage statistics"""
    
    latency_ms: float = 0.0
    """Total generation time in milliseconds"""
    
    retrieval_latency_ms: float = 0.0
    """Time spent on retrieval"""
    
    generation_latency_ms: float = 0.0
    """Time spent on LLM generation"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"RAGResponse(query='{self.query[:50]}...', "
            f"answer_length={len(self.answer)}, "
            f"sources={len(self.sources)}, "
            f"model='{self.model}')"
        )


class AnswerGenerator:
    """
    RAG Answer Generator combining semantic retrieval with LLM generation.
    
    This class orchestrates the complete RAG pipeline:
    1. Retrieves relevant document chunks using semantic search
    2. Formats context with source attribution
    3. Generates contextual answers using LLM
    4. Tracks citations and provides source transparency
    
    The generator is specialized for Peru guide content, with prompts
    optimized for historical, cultural, and geographical questions.
    
    Example:
        >>> from src.rag import AnswerGenerator
        >>> from src.retrieval_pipeline import SemanticRetriever
        >>> from src.llm import OpenAILLM, OpenAIConfig
        >>> 
        >>> retriever = SemanticRetriever(vector_store)
        >>> llm = OpenAILLM(OpenAIConfig(model="gpt-4"))
        >>> 
        >>> generator = AnswerGenerator(retriever=retriever, llm=llm)
        >>> 
        >>> response = generator.generate(
        ...     query="What are the Nazca Lines?",
        ...     top_k=3
        ... )
        >>> print(response.answer)
        >>> for source in response.sources:
        ...     print(f"- {source['title']}: {source['score']:.2f}")
    """
    
    # System prompt for Peru guide context
    SYSTEM_PROMPT = """You are a knowledgeable guide assistant specializing in Peru's history, culture, and geography.

Your role is to provide accurate, informative answers based on the provided context about Peru. You should:

1. **Answer based on context**: Use the provided source documents to formulate your answer. If the context doesn't contain enough information, say so clearly.

2. **Be informative and engaging**: Provide detailed explanations that educate the user about Peru's rich heritage.

3. **Cite sources naturally**: When referencing specific information, mention the source (e.g., "According to [Source 1]..." or "As described in [Source 2]...").

4. **Maintain accuracy**: Do not make up information. If you're unsure or the context is insufficient, acknowledge the limitation.

5. **Cultural sensitivity**: Show respect for Peru's indigenous cultures, historical sites, and traditions.

6. **Practical information**: When relevant, include practical details like locations, time periods, or visitor information.

Remember: You are helping people learn about and appreciate Peru's incredible cultural and natural heritage."""
    
    def __init__(
        self,
        retriever: SemanticRetriever,
        llm: BaseLLM,
        top_k: int = 5,
        include_metadata: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize Answer Generator.
        
        Args:
            retriever: Semantic retriever for finding relevant documents
            llm: Language model for generating answers
            top_k: Default number of documents to retrieve
            include_metadata: Whether to include metadata in context
            temperature: Override LLM temperature (if None, uses LLM's default)
            max_tokens: Override LLM max_tokens (if None, uses LLM's default)
        """
        self.retriever = retriever
        self.llm = llm
        self.top_k = top_k
        self.include_metadata = include_metadata
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        log.info(
            "answer_generator_initialized",
            llm_model=llm.config.model,
            top_k=top_k,
            include_metadata=include_metadata,
        )
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieval results into context string.
        
        Args:
            results: Retrieved document chunks (dicts from semantic retriever)
            
        Returns:
            Formatted context string with source attribution
        """
        if not results:
            return "No relevant context found."
        
        context_parts = []
        
        for idx, result in enumerate(results, 1):
            # Build source header
            source_header = f"[Source {idx}]"
            
            metadata = result.get("metadata", {})
            
            if self.include_metadata and metadata:
                # Add metadata like title, page, chapter
                meta_parts = []
                
                if "title" in metadata:
                    meta_parts.append(f"Title: {metadata['title']}")
                
                if "chapter" in metadata:
                    meta_parts.append(f"Chapter: {metadata['chapter']}")
                
                if "page" in metadata:
                    meta_parts.append(f"Page: {metadata['page']}")
                
                if meta_parts:
                    source_header += f" ({', '.join(meta_parts)})"
            
            # Add relevance score
            score = result.get("score", 0.0)
            source_header += f" [Relevance: {score:.2f}]"
            
            # Get content (try multiple keys for flexibility)
            content = (
                result.get("content") or 
                result.get("text") or 
                metadata.get("content") or
                metadata.get("text") or
                ""
            )
            
            # Build complete source entry
            context_parts.append(f"{source_header}\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> List[Message]:
        """
        Build prompt messages for LLM.
        
        Args:
            query: User's question
            context: Formatted context from retrieval
            
        Returns:
            List of messages for LLM
        """
        user_content = f"""Based on the following context about Peru, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If you reference specific information, cite the source number (e.g., [Source 1]). If the context doesn't contain enough information to fully answer the question, please say so."""
        
        return [
            Message(role="system", content=self.SYSTEM_PROMPT),
            Message(role="user", content=user_content),
        ]
    
    def _extract_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source information from retrieval results.
        
        Args:
            results: Retrieved document chunks (dicts from semantic retriever)
            
        Returns:
            List of source dictionaries with metadata and scores
        """
        sources = []
        
        for idx, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            
            # Get content (try multiple keys)
            content = (
                result.get("content") or 
                result.get("text") or 
                metadata.get("content") or
                metadata.get("text") or
                ""
            )
            
            source = {
                "source_id": idx,
                "content": content,
                "score": float(result.get("score", 0.0)),
                "metadata": metadata.copy() if metadata else {},
            }
            
            # Add document ID if available
            doc_id = result.get("id") or result.get("doc_id")
            if doc_id:
                source["doc_id"] = doc_id
            
            sources.append(source)
        
        return sources
    
    def generate(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        **llm_kwargs: Any,
    ) -> RAGResponse:
        """
        Generate answer for query using RAG pipeline.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve (overrides default)
            filters: Metadata filters for retrieval
            **llm_kwargs: Additional parameters for LLM generation
            
        Returns:
            RAGResponse with answer, sources, and metadata
        """
        total_start = time.time()
        
        # Use provided top_k or default
        k = top_k if top_k is not None else self.top_k
        
        log.info("rag_generation_started", query=query[:100], top_k=k)
        
        # Step 1: Retrieve relevant documents
        retrieval_start = time.time()
        results = self.retriever.retrieve(query=query, k=k, filters=filters)
        retrieval_latency = (time.time() - retrieval_start) * 1000
        
        log.info(
            "retrieval_completed",
            num_results=len(results),
            latency_ms=round(retrieval_latency, 2),
        )
        
        # Step 2: Format context
        context = self._format_context(results)
        
        # Step 3: Build prompt
        messages = self._build_prompt(query, context)
        
        # Step 4: Generate answer
        generation_start = time.time()
        
        # Build LLM parameters
        llm_params = llm_kwargs.copy()
        if self.temperature is not None and "temperature" not in llm_params:
            llm_params["temperature"] = self.temperature
        if self.max_tokens is not None and "max_tokens" not in llm_params:
            llm_params["max_tokens"] = self.max_tokens
        
        llm_response = self.llm.generate(messages, **llm_params)
        generation_latency = (time.time() - generation_start) * 1000
        
        total_latency = (time.time() - total_start) * 1000
        
        log.info(
            "rag_generation_completed",
            answer_length=len(llm_response.content),
            total_latency_ms=round(total_latency, 2),
            retrieval_latency_ms=round(retrieval_latency, 2),
            generation_latency_ms=round(generation_latency, 2),
        )
        
        # Step 5: Extract sources
        sources = self._extract_sources(results)
        
        # Build response
        return RAGResponse(
            answer=llm_response.content,
            sources=sources,
            query=query,
            model=llm_response.model,
            usage=llm_response.usage,
            latency_ms=total_latency,
            retrieval_latency_ms=retrieval_latency,
            generation_latency_ms=generation_latency,
            metadata={
                "top_k": k,
                "filters": filters,
                "llm_params": llm_params,
            },
        )
    
    def stream(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        **llm_kwargs: Any,
    ) -> Generator[StreamChunk, None, RAGResponse]:
        """
        Stream answer generation for query using RAG pipeline.
        
        This method performs retrieval first, then streams the LLM generation.
        The final chunk includes the complete RAGResponse with sources.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve (overrides default)
            filters: Metadata filters for retrieval
            **llm_kwargs: Additional parameters for LLM generation
            
        Yields:
            StreamChunk objects with incremental content
            
        Returns:
            Final RAGResponse (via StopIteration value)
        """
        total_start = time.time()
        
        # Use provided top_k or default
        k = top_k if top_k is not None else self.top_k
        
        log.info("rag_streaming_started", query=query[:100], top_k=k)
        
        # Step 1: Retrieve relevant documents
        retrieval_start = time.time()
        results = self.retriever.retrieve(query=query, k=k, filters=filters)
        retrieval_latency = (time.time() - retrieval_start) * 1000
        
        log.info(
            "retrieval_completed",
            num_results=len(results),
            latency_ms=round(retrieval_latency, 2),
        )
        
        # Step 2: Format context
        context = self._format_context(results)
        
        # Step 3: Build prompt
        messages = self._build_prompt(query, context)
        
        # Step 4: Stream generation
        generation_start = time.time()
        
        # Build LLM parameters
        llm_params = llm_kwargs.copy()
        if self.temperature is not None and "temperature" not in llm_params:
            llm_params["temperature"] = self.temperature
        if self.max_tokens is not None and "max_tokens" not in llm_params:
            llm_params["max_tokens"] = self.max_tokens
        
        # Stream chunks and collect full answer
        full_answer = ""
        chunk_count = 0
        
        for chunk in self.llm.stream(messages, **llm_params):
            full_answer += chunk.content
            chunk_count += 1
            yield chunk
        
        generation_latency = (time.time() - generation_start) * 1000
        total_latency = (time.time() - total_start) * 1000
        
        log.info(
            "rag_streaming_completed",
            chunks=chunk_count,
            answer_length=len(full_answer),
            total_latency_ms=round(total_latency, 2),
            retrieval_latency_ms=round(retrieval_latency, 2),
            generation_latency_ms=round(generation_latency, 2),
        )
        
        # Step 5: Extract sources
        sources = self._extract_sources(results)
        
        # Build final response
        final_response = RAGResponse(
            answer=full_answer,
            sources=sources,
            query=query,
            model=self.llm.config.model,
            usage=None,  # Usage not available from streaming
            latency_ms=total_latency,
            retrieval_latency_ms=retrieval_latency,
            generation_latency_ms=generation_latency,
            metadata={
                "top_k": k,
                "filters": filters,
                "llm_params": llm_params,
                "chunks": chunk_count,
            },
        )
        
        return final_response
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AnswerGenerator(llm={self.llm.config.model}, "
            f"top_k={self.top_k})"
        )
