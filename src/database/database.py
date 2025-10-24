"""
Database Module.

This module provides database connectivity and session management using
SQLAlchemy with async support.

Design Principles:
- Async/await for non-blocking database operations
- Connection pooling for performance
- Context managers for safe session handling
- Health checks and monitoring
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

# Global engine and session maker
_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """
    Get or create the global database engine.

    Returns:
        AsyncEngine: SQLAlchemy async engine.

    Example:
        >>> engine = get_engine()
        >>> async with engine.begin() as conn:
        ...     result = await conn.execute(text("SELECT 1"))
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        # Choose pooling strategy based on environment
        if settings.is_production:
            poolclass = QueuePool
            pool_kwargs = {
                "pool_size": settings.database.database_pool_size,
                "max_overflow": settings.database.database_max_overflow,
                "pool_timeout": settings.database.database_pool_timeout,
                "pool_recycle": settings.database.database_pool_recycle,
                "pool_pre_ping": True,  # Test connections before using
            }
        else:
            # Development: Use smaller pool
            poolclass = QueuePool
            pool_kwargs = {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "pool_pre_ping": True,
            }

        _engine = create_async_engine(
            settings.database.database_url,
            echo=settings.app.debug,  # Log SQL queries in debug mode
            poolclass=poolclass,
            **pool_kwargs,
        )

        logger.info(
            "Database engine created",
            extra={
                "host": settings.database.postgres_host,
                "port": settings.database.postgres_port,
                "database": settings.database.postgres_db,
                "pool_size": pool_kwargs.get("pool_size"),
            },
        )

    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the global session maker.

    Returns:
        async_sessionmaker: SQLAlchemy async session maker.

    Example:
        >>> session_maker = get_session_maker()
        >>> async with session_maker() as session:
        ...     result = await session.execute(text("SELECT 1"))
    """
    global _session_maker

    if _session_maker is None:
        engine = get_engine()
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info("Database session maker created")

    return _session_maker


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session with automatic cleanup.

    Yields:
        AsyncSession: Database session.

    Example:
        >>> async with get_session() as session:
        ...     result = await session.execute(text("SELECT 1"))
        ...     await session.commit()

    Note:
        Session is automatically closed after context exit.
        In case of exception, rollback is performed automatically.
    """
    session_maker = get_session_maker()
    session = session_maker()

    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        await session.close()


async def init_database() -> None:
    """
    Initialize database schema.

    Creates all tables defined in SQLAlchemy models.

    Example:
        >>> await init_database()

    Note:
        This is typically called during application startup.
        For production, use Alembic migrations instead.
    """
    engine = get_engine()

    async with engine.begin() as conn:
        # Create schema if not exists
        settings = get_settings()
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.database.database_schema}"))

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")


async def close_database() -> None:
    """
    Close database connections and dispose engine.

    Example:
        >>> await close_database()

    Note:
        This is typically called during application shutdown.
    """
    global _engine, _session_maker

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_maker = None

        logger.info("Database connections closed")


async def health_check() -> bool:
    """
    Check database connectivity.

    Returns:
        bool: True if database is accessible, False otherwise.

    Example:
        >>> is_healthy = await health_check()
        >>> if is_healthy:
        ...     print("Database is healthy")
    """
    try:
        async with get_session() as session:
            result = await session.execute(text("SELECT 1"))
            row = result.scalar()
            return row == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session.

    Example (FastAPI):
        >>> from fastapi import Depends
        >>> from src.database.database import get_db_session
        >>>
        >>> @app.get("/items")
        >>> async def get_items(session: AsyncSession = Depends(get_db_session)):
        ...     result = await session.execute(text("SELECT * FROM items"))
        ...     return result.fetchall()
    """
    async with get_session() as session:
        yield session


__all__ = [
    "Base",
    "get_engine",
    "get_session_maker",
    "get_session",
    "init_database",
    "close_database",
    "health_check",
    "get_db_session",
]
