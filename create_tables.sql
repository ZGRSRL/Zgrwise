-- ZgrWise Knowledge Management System Database Schema
-- Create all necessary tables for the system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    url VARCHAR NOT NULL,
    origin VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw TEXT,
    summary TEXT
);

-- Highlights table
CREATE TABLE IF NOT EXISTS highlights (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags JSONB DEFAULT '[]'::jsonb,
    summary TEXT,
    importance INTEGER DEFAULT 1,
    difficulty INTEGER DEFAULT 1,
    next_review TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    ease_factor FLOAT DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1
);

-- Embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    highlight_id INTEGER REFERENCES highlights(id) ON DELETE CASCADE,
    embedding VECTOR(384),
    model VARCHAR(50) DEFAULT 'BAAI/bge-small-en-v1.5',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RSS Feeds table
CREATE TABLE IF NOT EXISTS rss_feeds (
    id SERIAL PRIMARY KEY,
    url VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    description TEXT,
    last_fetched TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RSS Items table
CREATE TABLE IF NOT EXISTS rss_items (
    id SERIAL PRIMARY KEY,
    feed_id INTEGER REFERENCES rss_feeds(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    link VARCHAR NOT NULL,
    description TEXT,
    published_at TIMESTAMP,
    guid VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(feed_id, guid)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(type);
CREATE INDEX IF NOT EXISTS idx_sources_created_at ON sources(created_at);
CREATE INDEX IF NOT EXISTS idx_highlights_source_id ON highlights(source_id);
CREATE INDEX IF NOT EXISTS idx_highlights_next_review ON highlights(next_review);
CREATE INDEX IF NOT EXISTS idx_highlights_tags ON highlights USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_embeddings_source_id ON embeddings(source_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_highlight_id ON embeddings(highlight_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_url ON rss_feeds(url);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_active ON rss_feeds(is_active);
CREATE INDEX IF NOT EXISTS idx_rss_items_feed_id ON rss_items(feed_id);
CREATE INDEX IF NOT EXISTS idx_rss_items_published_at ON rss_items(published_at);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_sources_title_gin ON sources USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_highlights_text_gin ON highlights USING GIN(to_tsvector('english', text));
CREATE INDEX IF NOT EXISTS idx_highlights_context_gin ON highlights USING GIN(to_tsvector('english', context));

-- Insert some sample data
INSERT INTO sources (type, url, origin, title, author, summary) VALUES 
('web', 'https://example.com/article1', 'Example Site', 'Sample Article 1', 'John Doe', 'This is a sample article about knowledge management.'),
('web', 'https://example.com/article2', 'Example Site', 'Sample Article 2', 'Jane Smith', 'Another sample article about learning techniques.')
ON CONFLICT DO NOTHING;

INSERT INTO highlights (source_id, text, context, tags, summary, importance, difficulty) VALUES 
(1, 'Knowledge management is essential for personal growth.', 'In the introduction section', '["learning", "growth"]', 'Key insight about knowledge management', 3, 2),
(1, 'Spaced repetition helps with long-term retention.', 'In the methodology section', '["learning", "memory"]', 'Important learning technique', 4, 3),
(2, 'Active recall is more effective than passive reading.', 'In the research findings', '["learning", "study"]', 'Research-backed learning method', 5, 2)
ON CONFLICT DO NOTHING;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for rss_feeds
CREATE TRIGGER update_rss_feeds_updated_at BEFORE UPDATE ON rss_feeds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

