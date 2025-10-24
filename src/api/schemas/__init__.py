"""
Pydantic schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """Request schema for RAG query endpoint."""
    
    query: str = Field(
        ...,
        description="Question about Peru to answer using RAG",
        min_length=3,
        max_length=500,
        examples=["¿Cuáles son los platos típicos de Perú?"]
    )
    
    top_k: int = Field(
        default=3,
        description="Number of documents to retrieve",
        ge=1,
        le=10
    )
    
    llm_model: str = Field(
        default="openai",
        description="LLM provider to use for answer generation",
        examples=["openai", "anthropic", "deepseek", "huggingface", "azure"]
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Include source metadata in response"
    )
    
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata filters for retrieval",
        examples=[{"department": "Lima", "category": "gastronomy"}]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Qué es el ceviche peruano?",
                "top_k": 3,
                "llm_model": "openai",
                "include_metadata": True,
                "filters": {"category": "gastronomy"}
            }
        }
    )


class QueryResponse(BaseModel):
    """Response schema for RAG query endpoint."""
    
    answer: str = Field(
        ...,
        description="Generated answer with citations"
    )
    
    sources: List[str] = Field(
        ...,
        description="List of source identifiers used in the answer"
    )
    
    metadata: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Metadata for each retrieved source"
    )
    
    latency_ms: float = Field(
        ...,
        description="Total latency in milliseconds",
        ge=0
    )
    
    retrieval_latency_ms: Optional[float] = Field(
        default=None,
        description="Retrieval latency in milliseconds",
        ge=0
    )
    
    generation_latency_ms: Optional[float] = Field(
        default=None,
        description="Answer generation latency in milliseconds",
        ge=0
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer": "El ceviche peruano es un plato tradicional [Source 1]...",
                "sources": ["gastronomy_peru.pdf", "ceviche_history.pdf"],
                "metadata": [
                    {"department": "Lima", "category": "gastronomy"},
                    {"department": "Piura", "category": "gastronomy"}
                ],
                "latency_ms": 245.67,
                "retrieval_latency_ms": 12.34,
                "generation_latency_ms": 233.33
            }
        }
    )


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    
    status: str = Field(
        ...,
        description="Health status of the service"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    components: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual components"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "components": {
                    "vector_store": "healthy",
                    "embedder": "healthy",
                    "llm": "healthy"
                }
            }
        }
    )


class ModelsResponse(BaseModel):
    """Response schema for available models endpoint."""
    
    models: List[str] = Field(
        ...,
        description="List of available LLM models"
    )
    
    default_model: str = Field(
        ...,
        description="Default LLM model if none specified"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "models": ["openai", "anthropic", "deepseek", "huggingface", "azure"],
                "default_model": "openai"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Response schema for error responses."""
    
    error: str = Field(
        ...,
        description="Error message"
    )
    
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error information"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Invalid query",
                "detail": "Query must be between 3 and 500 characters"
            }
        }
    )
