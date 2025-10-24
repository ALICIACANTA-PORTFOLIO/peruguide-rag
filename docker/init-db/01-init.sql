-- PeruGuide RAG - Database Initialization Script
-- This script creates the necessary tables for analytics, feedback, and metadata

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for RAG-specific tables
CREATE SCHEMA IF NOT EXISTS rag;

-- ============================================================================
-- ANALYTICS & USAGE TRACKING
-- ============================================================================

-- Table for tracking queries and responses
CREATE TABLE IF NOT EXISTS rag.query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255),
    query_text TEXT NOT NULL,
    response_text TEXT,
    retrieved_chunks INT DEFAULT 0,
    response_time_ms FLOAT,
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Table for tracking retrieved documents
CREATE TABLE IF NOT EXISTS rag.retrieval_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_log_id UUID REFERENCES rag.query_logs(id) ON DELETE CASCADE,
    document_id VARCHAR(255),
    chunk_id VARCHAR(255),
    relevance_score FLOAT,
    rank INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ============================================================================
-- USER FEEDBACK
-- ============================================================================

-- Table for collecting user feedback on responses
CREATE TABLE IF NOT EXISTS rag.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_log_id UUID REFERENCES rag.query_logs(id) ON DELETE CASCADE,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_type VARCHAR(50),  -- 'helpful', 'not_helpful', 'incorrect', 'offensive'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ============================================================================
-- DOCUMENT METADATA CACHE
-- ============================================================================

-- Table for caching processed documents metadata
CREATE TABLE IF NOT EXISTS rag.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(255) UNIQUE NOT NULL,
    source_path TEXT,
    filename VARCHAR(500),
    document_type VARCHAR(50),
    chunk_count INT DEFAULT 0,
    embedding_model VARCHAR(100),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Table for document chunks
CREATE TABLE IF NOT EXISTS rag.document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES rag.documents(id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    chunk_index INT,
    chunk_text TEXT,
    token_count INT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EVALUATION RESULTS
-- ============================================================================

-- Table for storing RAGAS evaluation results
CREATE TABLE IF NOT EXISTS rag.evaluation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(255),
    query_text TEXT,
    response_text TEXT,
    ground_truth TEXT,
    faithfulness FLOAT,
    answer_relevancy FLOAT,
    context_precision FLOAT,
    context_recall FLOAT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Query logs indexes
CREATE INDEX IF NOT EXISTS idx_query_logs_session ON rag.query_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created ON rag.query_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_model ON rag.query_logs(model_name);

-- Retrieval logs indexes
CREATE INDEX IF NOT EXISTS idx_retrieval_logs_query ON rag.retrieval_logs(query_log_id);
CREATE INDEX IF NOT EXISTS idx_retrieval_logs_document ON rag.retrieval_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_retrieval_logs_score ON rag.retrieval_logs(relevance_score DESC);

-- Feedback indexes
CREATE INDEX IF NOT EXISTS idx_feedback_query ON rag.feedback(query_log_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON rag.feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON rag.feedback(created_at DESC);

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_doc_id ON rag.documents(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON rag.documents(processed_at DESC);

-- Document chunks indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document ON rag.document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_id ON rag.document_chunks(chunk_id);

-- Evaluation results indexes
CREATE INDEX IF NOT EXISTS idx_eval_run ON rag.evaluation_results(run_id);
CREATE INDEX IF NOT EXISTS idx_eval_created ON rag.evaluation_results(evaluated_at DESC);

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- View for query analytics
CREATE OR REPLACE VIEW rag.query_analytics AS
SELECT
    DATE_TRUNC('day', created_at) AS date,
    COUNT(*) AS total_queries,
    AVG(response_time_ms) AS avg_response_time_ms,
    AVG(retrieved_chunks) AS avg_retrieved_chunks,
    model_name
FROM rag.query_logs
GROUP BY DATE_TRUNC('day', created_at), model_name
ORDER BY date DESC;

-- View for feedback analytics
CREATE OR REPLACE VIEW rag.feedback_analytics AS
SELECT
    DATE_TRUNC('day', f.created_at) AS date,
    AVG(f.rating) AS avg_rating,
    COUNT(*) AS feedback_count,
    COUNT(*) FILTER (WHERE f.rating >= 4) AS positive_feedback,
    COUNT(*) FILTER (WHERE f.rating <= 2) AS negative_feedback
FROM rag.feedback f
GROUP BY DATE_TRUNC('day', f.created_at)
ORDER BY date DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to clean old logs (retention policy)
CREATE OR REPLACE FUNCTION rag.cleanup_old_logs(retention_days INT DEFAULT 90)
RETURNS TABLE(deleted_queries INT, deleted_retrievals INT) AS $$
DECLARE
    del_queries INT;
    del_retrievals INT;
BEGIN
    -- Delete old retrieval logs (cascades will handle related records)
    DELETE FROM rag.retrieval_logs
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS del_retrievals = ROW_COUNT;

    -- Delete old query logs
    DELETE FROM rag.query_logs
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS del_queries = ROW_COUNT;

    RETURN QUERY SELECT del_queries, del_retrievals;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS (adjust user as needed)
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA rag TO PUBLIC;

-- Grant select/insert/update/delete on all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA rag TO PUBLIC;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA rag TO PUBLIC;

-- ============================================================================
-- INITIAL DATA (Optional)
-- ============================================================================

-- Insert example metadata
INSERT INTO rag.documents (document_id, filename, document_type, metadata)
VALUES ('example-doc', 'example.pdf', 'pdf', '{"category": "example"}')
ON CONFLICT (document_id) DO NOTHING;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PeruGuide RAG database initialized successfully!';
    RAISE NOTICE 'Schema: rag';
    RAISE NOTICE 'Tables created: query_logs, retrieval_logs, feedback, documents, document_chunks, evaluation_results';
END $$;
