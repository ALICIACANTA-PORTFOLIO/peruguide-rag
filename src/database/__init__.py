"""Database module for PostgreSQL operations."""

from src.database.database import (
    Base,
    close_database,
    get_db_session,
    get_engine,
    get_session,
    get_session_maker,
    health_check,
    init_database,
)
from src.database.models import (
    Document,
    DocumentChunk,
    EvaluationResult,
    Feedback,
    QueryLog,
    RetrievalLog,
)

__all__ = [
    # Database
    "Base",
    "get_engine",
    "get_session_maker",
    "get_session",
    "init_database",
    "close_database",
    "health_check",
    "get_db_session",
    # Models
    "QueryLog",
    "RetrievalLog",
    "Feedback",
    "Document",
    "DocumentChunk",
    "EvaluationResult",
]
