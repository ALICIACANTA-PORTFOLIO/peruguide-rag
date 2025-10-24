"""
Configuration Management Module.

This module handles all application configuration using Pydantic Settings,
following 12-Factor App principles and best practices for configuration management.

Design Principles:
- Environment-based configuration (12-Factor App)
- Type-safe settings with validation
- Hierarchical configuration structure
- Secrets management ready
- Development/Production profiles
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application-level settings."""

    app_name: str = Field(default="PeruGuide AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()


class APISettings(BaseSettings):
    """API server settings."""

    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port", ge=1024, le=65535)
    api_reload: bool = Field(default=True, description="Enable auto-reload")
    api_workers: int = Field(default=1, description="Number of workers", ge=1)

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, ge=1)
    rate_limit_burst: int = Field(default=10, ge=1)


class LLMSettings(BaseSettings):
    """LLM model settings."""

    llm_model_name: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.3",
        description="LLM model name",
    )
    llm_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=512, ge=1, le=4096)
    llm_top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    llm_repetition_penalty: float = Field(default=1.1, ge=1.0, le=2.0)

    # API Keys (optional)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    mistral_api_key: Optional[str] = Field(default=None, description="Mistral API key")

    # Local model path
    llm_local_path: Optional[str] = Field(
        default="./models/mistral-7b-instruct",
        description="Path to local model",
    )


class EmbeddingSettings(BaseSettings):
    """Embedding model settings."""

    embedding_model_name: str = Field(
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        description="Embedding model name",
    )
    embedding_dimension: int = Field(default=768, ge=1, description="Embedding dimension")
    embedding_batch_size: int = Field(default=32, ge=1, description="Batch size")
    embedding_device: str = Field(default="cpu", description="Device: cpu or cuda")

    @field_validator("embedding_device")
    @classmethod
    def validate_device(cls, v: str) -> str:
        """Validate device."""
        allowed = ["cpu", "cuda"]
        if v not in allowed:
            raise ValueError(f"Device must be one of {allowed}")
        return v


class VectorStoreSettings(BaseSettings):
    """Vector store settings."""

    vector_store_type: str = Field(default="chroma", description="Vector store type: faiss or chroma")
    vector_store_path: str = Field(default="./data/vector_stores", description="Vector store path")

    # FAISS
    faiss_index_type: str = Field(default="IndexFlatL2")
    faiss_metric_type: str = Field(default="cosine")

    # ChromaDB
    chroma_collection_name: str = Field(default="peruguide_documents")
    chroma_persist_directory: str = Field(default="./data/vector_stores/chroma")

    @field_validator("vector_store_type")
    @classmethod
    def validate_vector_store_type(cls, v: str) -> str:
        """Validate vector store type."""
        allowed = ["faiss", "chroma"]
        if v not in allowed:
            raise ValueError(f"Vector store type must be one of {allowed}")
        return v


class RetrievalSettings(BaseSettings):
    """Retrieval settings."""

    retrieval_top_k: int = Field(default=5, ge=1, description="Top K documents to retrieve")
    retrieval_score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    retrieval_fetch_k: int = Field(default=20, ge=1)
    retrieval_search_type: str = Field(default="similarity", description="Search type: similarity or mmr")

    # Reranking
    enable_reranking: bool = Field(default=False)
    reranking_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    reranking_top_k: int = Field(default=3, ge=1)

    @field_validator("retrieval_search_type")
    @classmethod
    def validate_search_type(cls, v: str) -> str:
        """Validate search type."""
        allowed = ["similarity", "mmr"]
        if v not in allowed:
            raise ValueError(f"Search type must be one of {allowed}")
        return v


class DataProcessingSettings(BaseSettings):
    """Data processing settings (domain-agnostic)."""

    # Chunking
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=64, ge=0)
    chunk_separators: List[str] = Field(default=["\n\n", "\n", ".", " ", ""])

    # PDF Loading (configurable for any domain)
    pdf_source_dir: str = Field(default="./data/raw", description="PDF source directory")
    pdf_recursive: bool = Field(default=True, description="Recursive search")
    pdf_file_pattern: str = Field(default="*.pdf", description="File pattern")

    # Metadata Extraction (customizable per domain)
    extract_metadata: bool = Field(default=True)
    metadata_fields: List[str] = Field(
        default=["filename", "category", "region"],
        description="Metadata fields to extract (customizable)",
    )

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Validate chunk overlap is less than chunk size."""
        chunk_size = info.data.get("chunk_size", 512)
        if v >= chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v


class DatabaseSettings(BaseSettings):
    """Database settings (PostgreSQL)."""

    # PostgreSQL Connection
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432, ge=1024, le=65535)
    postgres_db: str = Field(default="peruguide")
    postgres_user: str = Field(default="peruguide_user")
    postgres_password: str = Field(default="changeme123")

    # Connection Pool
    database_pool_size: int = Field(default=10, ge=1)
    database_max_overflow: int = Field(default=20, ge=1)
    database_pool_timeout: int = Field(default=30, ge=1)
    database_pool_recycle: int = Field(default=3600, ge=60)

    # Schema
    database_schema: str = Field(default="rag")

    @property
    def database_url(self) -> str:
        """Construct database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Construct synchronous database URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


class CacheSettings(BaseSettings):
    """Cache settings (Redis)."""

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379, ge=1024, le=65535)
    redis_password: str = Field(default="changeme123")
    redis_db: int = Field(default=0, ge=0, le=15)

    # Cache Settings
    cache_enabled: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600, ge=1)
    cache_max_size_mb: int = Field(default=500, ge=1)

    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"


class EvaluationSettings(BaseSettings):
    """Evaluation settings (RAGAS)."""

    enable_ragas_evaluation: bool = Field(default=True)
    ragas_test_dataset_path: str = Field(default="./src/evaluation/test_dataset.json")
    ragas_metrics: List[str] = Field(
        default=["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    )

    # RAGAS LLM
    ragas_llm_model: str = Field(default="gpt-4")
    ragas_llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""

    # Prometheus
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090, ge=1024, le=65535)

    # Structured Logging
    log_format: str = Field(default="json", description="Log format: json or console")
    log_file_path: str = Field(default="./logs/peruguide.log")
    log_rotation: str = Field(default="1 day")
    log_retention: str = Field(default="30 days")

    # Sentry (optional)
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: Optional[str] = Field(default=None)

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        allowed = ["json", "console"]
        if v not in allowed:
            raise ValueError(f"Log format must be one of {allowed}")
        return v


class SecuritySettings(BaseSettings):
    """Security settings."""

    # API Authentication
    enable_auth: bool = Field(default=False)
    jwt_secret_key: Optional[str] = Field(default=None)
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24, ge=1)

    # API Keys
    api_key_header_name: str = Field(default="X-API-Key")
    valid_api_keys: List[str] = Field(default=[])


class TestingSettings(BaseSettings):
    """Testing settings."""

    pytest_timeout: int = Field(default=300, ge=1)
    test_coverage_threshold: int = Field(default=75, ge=0, le=100)
    enable_pre_commit_hooks: bool = Field(default=True)


class Settings(BaseSettings):
    """
    Main application settings.

    This class aggregates all configuration sections and loads from environment variables.
    Follows 12-Factor App principles for configuration management.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    # Configuration sections
    app: AppSettings = Field(default_factory=AppSettings)
    api: APISettings = Field(default_factory=APISettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    data_processing: DataProcessingSettings = Field(default_factory=DataProcessingSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    testing: TestingSettings = Field(default_factory=TestingSettings)

    def __init__(self, **kwargs):
        """Initialize settings with environment variables."""
        super().__init__(**kwargs)
        # Initialize nested settings from environment
        self.app = AppSettings()
        self.api = APISettings()
        self.llm = LLMSettings()
        self.embedding = EmbeddingSettings()
        self.vector_store = VectorStoreSettings()
        self.retrieval = RetrievalSettings()
        self.data_processing = DataProcessingSettings()
        self.database = DatabaseSettings()
        self.cache = CacheSettings()
        self.evaluation = EvaluationSettings()
        self.monitoring = MonitoringSettings()
        self.security = SecuritySettings()
        self.testing = TestingSettings()

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app.environment == "production"

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)."""
        data = self.model_dump()
        # Remove sensitive fields
        sensitive_fields = [
            "postgres_password",
            "redis_password",
            "openai_api_key",
            "anthropic_api_key",
            "mistral_api_key",
            "jwt_secret_key",
            "valid_api_keys",
        ]
        for field in sensitive_fields:
            if field in data:
                data[field] = "***REDACTED***"
        return data


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached singleton).

    Returns:
        Settings: Application settings instance.

    Example:
        >>> from src.config.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.app.app_name)
        'PeruGuide AI'
        >>> print(settings.database.database_url)
        'postgresql+asyncpg://...'
    """
    return Settings()


# Convenience exports
__all__ = [
    "Settings",
    "get_settings",
    "AppSettings",
    "APISettings",
    "LLMSettings",
    "EmbeddingSettings",
    "VectorStoreSettings",
    "RetrievalSettings",
    "DataProcessingSettings",
    "DatabaseSettings",
    "CacheSettings",
    "EvaluationSettings",
    "MonitoringSettings",
    "SecuritySettings",
    "TestingSettings",
]
