"""
Database Models.

SQLAlchemy models for analytics, feedback, and metadata storage.

Design Principles:
- Type-safe models with proper constraints
- JSON fields for flexible metadata
- Indexes for query performance
- Relationships for data integrity
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.database.database import Base


class QueryLog(Base):
    """Query and response tracking."""

    __tablename__ = "query_logs"
    __table_args__ = (
        Index("idx_query_logs_session", "session_id"),
        Index("idx_query_logs_created", "created_at"),
        Index("idx_query_logs_model", "model_name"),
        {"schema": "rag"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    retrieved_chunks = Column(Integer, default=0)
    response_time_ms = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships
    retrieval_logs = relationship("RetrievalLog", back_populates="query_log", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="query_log", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<QueryLog(id={self.id}, query='{self.query_text[:50]}...')>"


class RetrievalLog(Base):
    """Retrieved document tracking."""

    __tablename__ = "retrieval_logs"
    __table_args__ = (
        Index("idx_retrieval_logs_query", "query_log_id"),
        Index("idx_retrieval_logs_document", "document_id"),
        Index("idx_retrieval_logs_score", "relevance_score"),
        {"schema": "rag"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_log_id = Column(UUID(as_uuid=True), ForeignKey("rag.query_logs.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(255), nullable=True)
    chunk_id = Column(String(255), nullable=True)
    relevance_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships
    query_log = relationship("QueryLog", back_populates="retrieval_logs")

    def __repr__(self) -> str:
        return f"<RetrievalLog(id={self.id}, document_id={self.document_id}, score={self.relevance_score})>"


class Feedback(Base):
    """User feedback on responses."""

    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        Index("idx_feedback_query", "query_log_id"),
        Index("idx_feedback_rating", "rating"),
        Index("idx_feedback_created", "created_at"),
        {"schema": "rag"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_log_id = Column(UUID(as_uuid=True), ForeignKey("rag.query_logs.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback_text = Column(Text, nullable=True)
    feedback_type = Column(String(50), nullable=True)  # 'helpful', 'not_helpful', 'incorrect', 'offensive'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships
    query_log = relationship("QueryLog", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, rating={self.rating}, type={self.feedback_type})>"


class Document(Base):
    """Document metadata cache."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_documents_doc_id", "document_id", unique=True),
        Index("idx_documents_processed", "processed_at"),
        {"schema": "rag"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String(255), unique=True, nullable=False)
    source_path = Column(Text, nullable=True)
    filename = Column(String(500), nullable=True)
    document_type = Column(String(50), nullable=True)
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(100), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, chunks={self.chunk_count})>"


class DocumentChunk(Base):
    """Document chunk storage."""

    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("idx_chunks_document", "document_id"),
        Index("idx_chunks_chunk_id", "chunk_id", unique=True),
        {"schema": "rag"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("rag.documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(255), unique=True, nullable=False)
    chunk_index = Column(Integer, nullable=True)
    chunk_text = Column(Text, nullable=True)
    token_count = Column(Integer, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, chunk_id={self.chunk_id}, tokens={self.token_count})>"


class EvaluationResult(Base):
    """RAGAS evaluation results."""

    __tablename__ = "evaluation_results"
    __table_args__ = (
        Index("idx_eval_run", "run_id"),
        Index("idx_eval_created", "evaluated_at"),
        {"schema": "rag"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(255), nullable=True)
    query_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    ground_truth = Column(Text, nullable=True)
    faithfulness = Column(Float, nullable=True)
    answer_relevancy = Column(Float, nullable=True)
    context_precision = Column(Float, nullable=True)
    context_recall = Column(Float, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<EvaluationResult(id={self.id}, run_id={self.run_id})>"


__all__ = [
    "QueryLog",
    "RetrievalLog",
    "Feedback",
    "Document",
    "DocumentChunk",
    "EvaluationResult",
]
