-- Database performance tuning for ZgrWise
-- This script configures PostgreSQL for optimal performance

-- =============================================================================
-- CONNECTION AND MEMORY SETTINGS
-- =============================================================================

-- These settings should be configured in postgresql.conf
-- They are documented here for reference

-- shared_buffers = 256MB                    -- 25% of RAM for small instances
-- effective_cache_size = 1GB                -- 75% of RAM
-- work_mem = 4MB                            -- For sorting and hash operations
-- maintenance_work_mem = 64MB               -- For maintenance operations
-- random_page_cost = 1.1                    -- For SSD storage
-- effective_io_concurrency = 200            -- For SSD storage

-- =============================================================================
-- QUERY OPTIMIZATION
-- =============================================================================

-- Enable query optimization features
SET enable_hashjoin = on;
SET enable_mergejoin = on;
SET enable_nestloop = on;
SET enable_seqscan = on;
SET enable_indexscan = on;
SET enable_indexonlyscan = on;
SET enable_bitmapscan = on;

-- =============================================================================
-- VACUUM AND ANALYZE SETTINGS
-- =============================================================================

-- Configure autovacuum for better performance
ALTER TABLE highlights SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE highlights SET (autovacuum_analyze_scale_factor = 0.05);
ALTER TABLE highlights SET (autovacuum_vacuum_threshold = 50);
ALTER TABLE highlights SET (autovacuum_analyze_threshold = 50);

ALTER TABLE sources SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE sources SET (autovacuum_analyze_scale_factor = 0.05);

ALTER TABLE rss_feeds SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE rss_feeds SET (autovacuum_analyze_scale_factor = 0.05);

ALTER TABLE rss_articles SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE rss_articles SET (autovacuum_analyze_scale_factor = 0.05);

-- =============================================================================
-- TEXT SEARCH CONFIGURATION
-- =============================================================================

-- Create custom text search configuration for better search
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS zgrwise_english (COPY = english);

-- Add custom dictionary for technical terms
-- This would require additional dictionary files
-- ALTER TEXT SEARCH CONFIGURATION zgrwise_english
--     ALTER MAPPING FOR asciiword, asciihword, hword_asciipart
--     WITH english_stem;

-- =============================================================================
-- MATERIALIZED VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Materialized view for highlight statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS highlight_stats AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    source_type,
    COUNT(*) as highlight_count,
    COUNT(DISTINCT source_id) as unique_sources,
    AVG(LENGTH(text)) as avg_text_length
FROM highlights h
JOIN sources s ON h.source_id = s.id
GROUP BY DATE_TRUNC('day', created_at), source_type;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_highlight_stats_date_type 
ON highlight_stats (date, source_type);

-- Materialized view for review statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS review_stats AS
SELECT 
    DATE_TRUNC('day', session_date) as date,
    user_id,
    COUNT(*) as sessions_count,
    COUNT(DISTINCT highlight_id) as unique_highlights,
    AVG(score) as avg_score
FROM review_sessions
GROUP BY DATE_TRUNC('day', session_date), user_id;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_review_stats_date_user 
ON review_stats (date, user_id);

-- =============================================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- =============================================================================

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY highlight_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY review_stats;
END;
$$ LANGUAGE plpgsql;

-- Function to get highlight statistics
CREATE OR REPLACE FUNCTION get_highlight_stats(
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    date DATE,
    source_type VARCHAR,
    highlight_count BIGINT,
    unique_sources BIGINT,
    avg_text_length NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        hs.date::DATE,
        hs.source_type,
        hs.highlight_count,
        hs.unique_sources,
        hs.avg_text_length
    FROM highlight_stats hs
    WHERE 
        (start_date IS NULL OR hs.date >= start_date) AND
        (end_date IS NULL OR hs.date <= end_date)
    ORDER BY hs.date DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Function to update highlight stats when highlights change
CREATE OR REPLACE FUNCTION update_highlight_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Refresh materialized view asynchronously
    PERFORM pg_notify('refresh_stats', 'highlight_stats');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for highlight changes
DROP TRIGGER IF EXISTS trigger_update_highlight_stats ON highlights;
CREATE TRIGGER trigger_update_highlight_stats
    AFTER INSERT OR UPDATE OR DELETE ON highlights
    FOR EACH STATEMENT
    EXECUTE FUNCTION update_highlight_stats();

-- =============================================================================
-- MONITORING QUERIES
-- =============================================================================

-- Query to check index usage
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_scan < 100 THEN 'LOW_USAGE'
        ELSE 'ACTIVE'
    END as usage_status
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Query to check table sizes
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =============================================================================
-- CLEANUP PROCEDURES
-- =============================================================================

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data(
    days_to_keep INTEGER DEFAULT 365
)
RETURNS TABLE (
    table_name TEXT,
    deleted_count BIGINT
) AS $$
DECLARE
    cutoff_date TIMESTAMP;
    result RECORD;
BEGIN
    cutoff_date := NOW() - (days_to_keep || ' days')::INTERVAL;
    
    -- Clean up old review sessions
    DELETE FROM review_sessions WHERE session_date < cutoff_date;
    GET DIAGNOSTICS result.deleted_count = ROW_COUNT;
    result.table_name := 'review_sessions';
    RETURN NEXT result;
    
    -- Clean up old export jobs
    DELETE FROM export_jobs WHERE created_at < cutoff_date AND status = 'completed';
    GET DIAGNOSTICS result.deleted_count = ROW_COUNT;
    result.table_name := 'export_jobs';
    RETURN NEXT result;
    
    -- Clean up old highlights (optional - be careful!)
    -- DELETE FROM highlights WHERE created_at < cutoff_date;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;
