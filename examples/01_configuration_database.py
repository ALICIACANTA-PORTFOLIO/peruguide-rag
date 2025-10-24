"""
Example: Database Configuration and Usage.

This script demonstrates how to:
1. Load configuration from .env
2. Connect to PostgreSQL
3. Perform basic database operations
4. Use the configuration in a domain-agnostic way
"""

import asyncio
import logging

from sqlalchemy import text

from src.config.settings import get_settings
from src.database import (
    Document,
    QueryLog,
    get_session,
    health_check,
    init_database,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def example_configuration():
    """Example: Using configuration settings."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Configuration Management")
    logger.info("=" * 60)

    # Get settings (cached singleton)
    settings = get_settings()

    # Access configuration sections
    logger.info(f"App Name: {settings.app.app_name}")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug Mode: {settings.app.debug}")

    # Database configuration
    logger.info(f"\nDatabase Configuration:")
    logger.info(f"  Host: {settings.database.postgres_host}")
    logger.info(f"  Port: {settings.database.postgres_port}")
    logger.info(f"  Database: {settings.database.postgres_db}")
    logger.info(f"  User: {settings.database.postgres_user}")
    logger.info(f"  Connection URL: {settings.database.database_url[:50]}...")

    # Data processing configuration (domain-agnostic)
    logger.info(f"\nData Processing Configuration:")
    logger.info(f"  PDF Source: {settings.data_processing.pdf_source_dir}")
    logger.info(f"  Chunk Size: {settings.data_processing.chunk_size}")
    logger.info(f"  Chunk Overlap: {settings.data_processing.chunk_overlap}")
    logger.info(f"  Metadata Fields: {settings.data_processing.metadata_fields}")

    # Environment checks
    logger.info(f"\nEnvironment Checks:")
    logger.info(f"  Is Development: {settings.is_development}")
    logger.info(f"  Is Production: {settings.is_production}")


async def example_health_check():
    """Example: Database health check."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 2: Database Health Check")
    logger.info("=" * 60)

    is_healthy = await health_check()
    if is_healthy:
        logger.info("✅ Database is healthy and accessible")
    else:
        logger.error("❌ Database health check failed")
        logger.error("Make sure Docker containers are running:")
        logger.error("  docker-compose up -d postgres")


async def example_database_operations():
    """Example: Basic database operations."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 3: Database Operations")
    logger.info("=" * 60)

    # Initialize database (create tables)
    logger.info("Initializing database schema...")
    await init_database()
    logger.info("✅ Database schema initialized")

    # Example 1: Insert query log
    logger.info("\nInserting query log...")
    async with get_session() as session:
        query_log = QueryLog(
            session_id="example-session-123",
            query_text="¿Cuáles son los mejores lugares turísticos en Cusco?",
            response_text="Los mejores lugares turísticos en Cusco incluyen Machu Picchu, el Valle Sagrado...",
            retrieved_chunks=5,
            response_time_ms=350.5,
            model_name="mistral-7b",
            metadata={"language": "es", "source": "example"},
        )
        session.add(query_log)
        await session.commit()
        logger.info(f"✅ Query log inserted with ID: {query_log.id}")

    # Example 2: Insert document metadata
    logger.info("\nInserting document metadata...")
    async with get_session() as session:
        document = Document(
            document_id="example-doc-001",
            source_path="./data/raw/example.pdf",
            filename="example.pdf",
            document_type="pdf",
            chunk_count=10,
            embedding_model="paraphrase-multilingual-mpnet-base-v2",
            metadata={
                "category": "tourism",
                "region": "cusco",
                "language": "es",
            },
        )
        session.add(document)
        await session.commit()
        logger.info(f"✅ Document inserted with ID: {document.id}")

    # Example 3: Query data
    logger.info("\nQuerying data...")
    async with get_session() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM rag.query_logs")
        )
        count = result.scalar()
        logger.info(f"✅ Total query logs: {count}")

        result = await session.execute(
            text("SELECT COUNT(*) FROM rag.documents")
        )
        count = result.scalar()
        logger.info(f"✅ Total documents: {count}")


async def example_domain_agnostic_usage():
    """Example: Domain-agnostic configuration usage."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 4: Domain-Agnostic Configuration")
    logger.info("=" * 60)

    settings = get_settings()

    logger.info("This configuration works for ANY domain:")
    logger.info(f"  - Tourism PDFs from: {settings.data_processing.pdf_source_dir}")
    logger.info(f"  - Legal documents from: {settings.data_processing.pdf_source_dir}")
    logger.info(f"  - Academic papers from: {settings.data_processing.pdf_source_dir}")
    logger.info("\nSimply change PDF_SOURCE_DIR in .env to point to your data!")

    logger.info("\nMetadata fields are customizable:")
    logger.info(f"  Current: {settings.data_processing.metadata_fields}")
    logger.info("  Tourism: ['filename', 'category', 'region', 'language']")
    logger.info("  Legal: ['filename', 'case_number', 'jurisdiction', 'date']")
    logger.info("  Academic: ['filename', 'author', 'journal', 'year']")


async def main():
    """Run all examples."""
    logger.info("\n" + "=" * 60)
    logger.info("PeruGuide RAG - Configuration & Database Examples")
    logger.info("=" * 60)

    try:
        # Example 1: Configuration
        await example_configuration()

        # Example 2: Health check
        await example_health_check()

        # Example 3: Database operations
        # Note: Make sure Docker containers are running!
        try:
            await example_database_operations()
        except Exception as e:
            logger.error(f"Database operations failed: {e}")
            logger.error("Make sure to start Docker containers:")
            logger.error("  docker-compose up -d postgres")

        # Example 4: Domain-agnostic usage
        await example_domain_agnostic_usage()

        logger.info("\n" + "=" * 60)
        logger.info("✅ All examples completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
