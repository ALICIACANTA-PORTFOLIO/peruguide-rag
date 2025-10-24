"""
FastAPI application for PeruGuide RAG system.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from src.api.routes import query, health, models
from src.api.dependencies import get_vector_store, get_embedder

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Initialize components on startup and cleanup on shutdown.
    """
    logger.info("application_startup", version="1.0.0")
    
    # Initialize components (singletons via lru_cache)
    try:
        embedder = get_embedder()
        vector_store = get_vector_store()
        logger.info(
            "components_initialized",
            embedder_dim=embedder.get_dimension(),
            num_vectors=vector_store.num_vectors
        )
    except Exception as e:
        logger.error("component_initialization_failed", error=str(e))
        raise
    
    yield  # Server runs here
    
    logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title="PeruGuide RAG API",
    description="Retrieval-Augmented Generation system for Peru travel information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to PeruGuide RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
