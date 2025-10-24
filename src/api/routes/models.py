"""
Models route for available LLM models.
"""

from fastapi import APIRouter
import structlog

from src.api.schemas import ModelsResponse
from src.api.dependencies import get_available_models, get_default_model

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List available models",
    description="Get list of available LLM models for answer generation"
)
async def list_models() -> ModelsResponse:
    """
    List available LLM models.
    
    Returns:
        ModelsResponse: List of available models and default model
    """
    logger.info("models_list_requested")
    
    models = get_available_models()
    default_model = get_default_model()
    
    logger.info("models_list_returned", num_models=len(models), default=default_model)
    
    return ModelsResponse(
        models=models,
        default_model=default_model
    )
