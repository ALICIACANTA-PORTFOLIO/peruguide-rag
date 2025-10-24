"""
RAG Module

This module implements the complete Retrieval-Augmented Generation pipeline,
combining semantic retrieval with LLM generation to provide contextual answers
about Peru's history, culture, and geography.

Components:
    - AnswerGenerator: Main RAG orchestrator combining retrieval + generation
    - Citation tracking for transparent source attribution
    - Streaming support for real-time responses

Example:
    >>> from src.rag import AnswerGenerator
    >>> from src.retrieval_pipeline import SemanticRetriever
    >>> from src.llm import OpenAILLM, OpenAIConfig
    >>> 
    >>> # Setup components
    >>> retriever = SemanticRetriever(vector_store)
    >>> llm_config = OpenAIConfig(model="gpt-4")
    >>> llm = OpenAILLM(llm_config)
    >>> 
    >>> # Create RAG generator
    >>> generator = AnswerGenerator(retriever=retriever, llm=llm)
    >>> 
    >>> # Generate answer with citations
    >>> response = generator.generate(
    ...     query="What are the main Inca archaeological sites?",
    ...     top_k=5
    ... )
    >>> print(response.answer)
    >>> print(response.sources)
"""

from src.rag.answer_generator import AnswerGenerator, RAGResponse

__all__ = [
    "AnswerGenerator",
    "RAGResponse",
]
