"""
FastAPI dependencies for RAG components.
"""

from functools import lru_cache
from typing import Optional
import structlog

from src.embedding_pipeline.models.sentence_transformer import SentenceTransformerEmbedder
from src.vector_store.faiss_store import FaissVectorStore
from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever
from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM
from src.llm.deepseek_llm import DeepSeekLLM
from src.llm.azure_openai_llm import AzureOpenAILLM
from src.llm.huggingface_llm import HuggingFaceLLM
from src.rag.answer_generator import AnswerGenerator

logger = structlog.get_logger(__name__)


@lru_cache()
def get_embedder() -> SentenceTransformerEmbedder:
    """
    Get embedder instance (singleton).
    
    Returns:
        SentenceTransformerEmbedder: Configured embedder instance
    """
    logger.info("initializing_embedder", model="sentence-transformers/all-MiniLM-L6-v2")
    embedder = SentenceTransformerEmbedder(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"  # Use GPU if available
    )
    logger.info("embedder_initialized", dimension=embedder.get_dimension())
    return embedder


@lru_cache()
def get_vector_store() -> FaissVectorStore:
    """
    Get vector store instance (singleton).
    
    Returns:
        FaissVectorStore: Configured FAISS vector store
    """
    embedder = get_embedder()
    dimension = embedder.get_dimension()
    
    logger.info("initializing_vector_store", dimension=dimension)
    vector_store = FaissVectorStore(dimension=dimension)
    
    # TODO: Load pre-built index if available
    # vector_store.load("path/to/index")
    
    logger.info("vector_store_initialized", num_vectors=vector_store.num_vectors)
    return vector_store


@lru_cache()
def get_retriever() -> SemanticRetriever:
    """
    Get semantic retriever instance (singleton).
    
    Returns:
        SemanticRetriever: Configured semantic retriever
    """
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    logger.info("initializing_retriever")
    retriever = SemanticRetriever(
        embedder=embedder,
        vector_store=vector_store
    )
    logger.info("retriever_initialized")
    return retriever


def get_llm(model: str = "openai") -> Optional[object]:
    """
    Get LLM instance based on model name.
    
    Args:
        model: LLM provider name ("openai", "anthropic", "deepseek", etc.)
    
    Returns:
        BaseLLM: Configured LLM instance
        
    Raises:
        ValueError: If model is not supported
    """
    logger.info("initializing_llm", model=model)
    
    llm_map = {
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "deepseek": DeepSeekLLM,
        "azure": AzureOpenAILLM,
        "huggingface": HuggingFaceLLM,
    }
    
    if model not in llm_map:
        raise ValueError(f"Unsupported LLM model: {model}. Available: {list(llm_map.keys())}")
    
    llm_class = llm_map[model]
    llm = llm_class()
    
    logger.info("llm_initialized", model=model)
    return llm


def get_answer_generator(
    llm_model: str = "openai",
    top_k: int = 3,
    include_metadata: bool = True
) -> AnswerGenerator:
    """
    Get answer generator instance.
    
    Args:
        llm_model: LLM provider name
        top_k: Number of documents to retrieve
        include_metadata: Whether to include source metadata
    
    Returns:
        AnswerGenerator: Configured answer generator
    """
    retriever = get_retriever()
    llm = get_llm(llm_model)
    
    logger.info(
        "initializing_answer_generator",
        llm_model=llm_model,
        top_k=top_k,
        include_metadata=include_metadata
    )
    
    generator = AnswerGenerator(
        retriever=retriever,
        llm=llm,
        top_k=top_k,
        include_metadata=include_metadata
    )
    
    logger.info("answer_generator_initialized")
    return generator


def get_available_models() -> list[str]:
    """
    Get list of available LLM models.
    
    Returns:
        List of available model names
    """
    return ["openai", "anthropic", "deepseek", "azure", "huggingface"]


def get_default_model() -> str:
    """
    Get default LLM model.
    
    Returns:
        Default model name
    """
    return "openai"
