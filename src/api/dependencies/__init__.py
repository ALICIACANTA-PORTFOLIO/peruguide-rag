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
from src.llm.config import OpenAIConfig, AnthropicConfig, DeepSeekConfig, AzureOpenAIConfig, HuggingFaceConfig
from src.rag.answer_generator import AnswerGenerator

logger = structlog.get_logger(__name__)


@lru_cache()
def get_embedder() -> SentenceTransformerEmbedder:
    """
    Get embedder instance (singleton).
    
    Returns:
        SentenceTransformerEmbedder: Configured embedder instance
    """
    logger.info("initializing_embedder", model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    embedder = SentenceTransformerEmbedder(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
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
    from pathlib import Path
    
    embedder = get_embedder()
    dimension = embedder.get_dimension()
    
    logger.info("initializing_vector_store", dimension=dimension)
    vector_store = FaissVectorStore(dimension=dimension)
    
    # Load pre-built index if available
    index_path = Path("data/vector_stores/faiss_peru_guide.index")
    if index_path.exists():
        logger.info("loading_vector_store", path=str(index_path))
        vector_store.load(str(index_path))
        logger.info("vector_store_loaded", num_vectors=vector_store.index.ntotal)
    else:
        logger.warning("vector_store_index_not_found", path=str(index_path))
    
    logger.info("vector_store_initialized", num_vectors=vector_store.index.ntotal)
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
    
    # Map of model names to (LLM class, Config class) tuples
    # Create configs lazily to avoid initialization errors on import
    llm_map = {
        "openai": (OpenAILLM, OpenAIConfig),
        "anthropic": (AnthropicLLM, AnthropicConfig),
        "deepseek": (DeepSeekLLM, DeepSeekConfig),
        "azure": (AzureOpenAILLM, AzureOpenAIConfig),
        "huggingface": (HuggingFaceLLM, HuggingFaceConfig),
    }
    
    if model not in llm_map:
        raise ValueError(f"Unsupported LLM model: {model}. Available: {list(llm_map.keys())}")
    
    try:
        llm_class, config_class = llm_map[model]
        logger.info("creating_llm_config", model=model, config_class=config_class.__name__)
        config = config_class()  # Create config instance here
        logger.info("llm_config_created", model=model)
        
        logger.info("creating_llm_instance", model=model)
        llm = llm_class(config)
        logger.info("llm_initialized", model=model)
        return llm
    except Exception as e:
        logger.error("llm_initialization_failed", model=model, error=str(e), exc_info=True)
        raise


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
    return "huggingface"
