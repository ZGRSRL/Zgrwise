-- Database optimization indexes for ZgrWise
-- This script creates optimized indexes for better performance

-- =============================================================================
-- HIGHLIGHTS TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for text search on highlights
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_text_gin 
ON highlights USING gin(to_tsvector('english', text));

-- Index for source_id lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_source_id 
ON highlights (source_id);

-- Index for created_at for time-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_created_at 
ON highlights (created_at DESC);

-- Index for tags array operations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_tags_gin 
ON highlights USING gin(tags);

-- Index for review scheduling
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_next_review 
ON highlights (next_review) WHERE next_review IS NOT NULL;

-- Composite index for source + created_at
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_source_created 
ON highlights (source_id, created_at DESC);

-- =============================================================================
-- SOURCES TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for URL lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sources_url 
ON sources (url);

-- Index for source_type filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sources_type 
ON sources (source_type);

-- Index for created_at for time-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sources_created_at 
ON highlights (created_at DESC);

-- Index for title search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sources_title_gin 
ON sources USING gin(to_tsvector('english', title));

-- =============================================================================
-- RSS FEEDS TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for URL lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_feeds_url 
ON rss_feeds (url);

-- Index for active feeds
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_feeds_active 
ON rss_feeds (is_active) WHERE is_active = true;

-- Index for last_updated for scheduling
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_feeds_last_updated 
ON rss_feeds (last_updated);

-- =============================================================================
-- RSS ARTICLES TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for feed_id lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_articles_feed_id 
ON rss_articles (feed_id);

-- Index for published_date for time-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_articles_published 
ON rss_articles (published_date DESC);

-- Index for URL uniqueness
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_articles_url_unique 
ON rss_articles (url);

-- Index for title search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_articles_title_gin 
ON rss_articles USING gin(to_tsvector('english', title));

-- =============================================================================
-- EMBEDDINGS TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for highlight_id lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embeddings_highlight_id 
ON embeddings (highlight_id);

-- Index for model filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embeddings_model 
ON embeddings (model);

-- =============================================================================
-- REVIEW SESSIONS TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for user_id lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_review_sessions_user_id 
ON review_sessions (user_id);

-- Index for session_date for time-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_review_sessions_date 
ON review_sessions (session_date DESC);

-- Composite index for user + date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_review_sessions_user_date 
ON review_sessions (user_id, session_date DESC);

-- =============================================================================
-- EXPORT JOBS TABLE OPTIMIZATIONS
-- =============================================================================

-- Index for status filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_export_jobs_status 
ON export_jobs (status);

-- Index for created_at for time-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_export_jobs_created_at 
ON export_jobs (created_at DESC);

-- Index for user_id lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_export_jobs_user_id 
ON export_jobs (user_id);

-- =============================================================================
-- VECTOR SIMILARITY OPTIMIZATIONS (pgvector)
-- =============================================================================

-- Index for vector similarity search (if using pgvector)
-- Note: This requires pgvector extension to be installed
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embeddings_vector_cosine 
-- ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Alternative HNSW index for better recall
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embeddings_vector_hnsw 
-- ON embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- =============================================================================
-- PARTIAL INDEXES FOR COMMON QUERIES
-- =============================================================================

-- Index for highlights that need review
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_needs_review 
ON highlights (next_review) WHERE next_review <= NOW();

-- Index for recent highlights (last 30 days)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_highlights_recent 
ON highlights (created_at DESC) WHERE created_at >= NOW() - INTERVAL '30 days';

-- Index for active RSS feeds with recent updates
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rss_feeds_active_recent 
ON rss_feeds (last_updated DESC) WHERE is_active = true AND last_updated >= NOW() - INTERVAL '7 days';

-- =============================================================================
-- STATISTICS UPDATE
-- =============================================================================

-- Update table statistics for better query planning
ANALYZE highlights;
ANALYZE sources;
ANALYZE rss_feeds;
ANALYZE rss_articles;
ANALYZE embeddings;
ANALYZE review_sessions;
ANALYZE export_jobs;
