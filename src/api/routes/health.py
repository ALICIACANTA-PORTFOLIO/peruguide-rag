"""
Health check route.
"""

from fastapi import APIRouter
import structlog

from src.api.schemas import HealthResponse
from src.api.dependencies import get_embedder, get_vector_store, get_retriever

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the API and its components"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Health status of service and components
    """
    logger.info("health_check_requested")
    
    components = {}
    
    try:
        # Check embedder
        embedder = get_embedder()
        components["embedder"] = "healthy" if embedder else "unhealthy"
    except Exception as e:
        logger.warning("embedder_check_failed", error=str(e))
        components["embedder"] = "unhealthy"
    
    try:
        # Check vector store
        vector_store = get_vector_store()
        components["vector_store"] = "healthy" if vector_store else "unhealthy"
        components["num_vectors"] = str(vector_store.num_vectors)
    except Exception as e:
        logger.warning("vector_store_check_failed", error=str(e))
        components["vector_store"] = "unhealthy"
    
    try:
        # Check retriever
        retriever = get_retriever()
        components["retriever"] = "healthy" if retriever else "unhealthy"
    except Exception as e:
        logger.warning("retriever_check_failed", error=str(e))
        components["retriever"] = "unhealthy"
    
    # Overall status
    status = "healthy" if all(
        v == "healthy" or v.isdigit() 
        for v in components.values()
    ) else "degraded"
    
    logger.info("health_check_completed", status=status, components=components)
    
    return HealthResponse(
        status=status,
        version="1.0.0",
        components=components
    )
