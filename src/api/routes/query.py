"""
Query route for RAG system.
"""

from fastapi import APIRouter, HTTPException, status
import structlog

from src.api.schemas import QueryRequest, QueryResponse, ErrorResponse
from src.api.dependencies import get_answer_generator

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Query the RAG system",
    description="Send a question about Peru and receive an AI-generated answer with sources"
)
async def query_rag(request: QueryRequest) -> QueryResponse:
    """
    Query the RAG system with a question about Peru.
    
    Args:
        request: Query request with question and parameters
    
    Returns:
        QueryResponse: Generated answer with sources and metadata
    
    Raises:
        HTTPException: If query processing fails
    """
    logger.info(
        "query_received",
        query_preview=request.query[:50],
        top_k=request.top_k,
        llm_model=request.llm_model
    )
    
    try:
        # Get answer generator with specified parameters
        generator = get_answer_generator(
            llm_model=request.llm_model,
            top_k=request.top_k,
            include_metadata=request.include_metadata
        )
        
        # Generate answer
        response = generator.generate(
            query=request.query,
            k=request.top_k,
            filters=request.filters
        )
        
        logger.info(
            "query_completed",
            answer_length=len(response.answer),
            num_sources=len(response.sources),
            latency_ms=response.latency_ms
        )
        
        # Build API response
        api_response = QueryResponse(
            answer=response.answer,
            sources=response.sources,
            metadata=response.metadata if request.include_metadata else None,
            latency_ms=response.latency_ms,
            retrieval_latency_ms=getattr(response, 'retrieval_latency_ms', None),
            generation_latency_ms=getattr(response, 'generation_latency_ms', None)
        )
        
        return api_response
        
    except ValueError as e:
        logger.warning("invalid_request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid request", "detail": str(e)}
        )
    
    except Exception as e:
        logger.error("query_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Query processing failed", "detail": str(e)}
        )
