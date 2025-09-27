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
    note TEXT, -- Changed from context to note to match SQLAlchemy model
    location VARCHAR, -- Added to match SQLAlchemy model
    color VARCHAR, -- Added to match SQLAlchemy model
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
    object_type VARCHAR(20) NOT NULL, -- 'source' or 'highlight' to match SQLAlchemy model
    object_id INTEGER NOT NULL, -- References either source_id or highlight_id
    model VARCHAR(50) DEFAULT 'BAAI/bge-small-en-v1.5',
    vector VECTOR(384), -- Changed from embedding to vector to match SQLAlchemy model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RSS Feeds table
CREATE TABLE IF NOT EXISTS rss_feeds (
    id SERIAL PRIMARY KEY,
    url VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    description TEXT,
    last_checked TIMESTAMP, -- Changed from last_fetched to last_checked to match SQLAlchemy model
    is_active BOOLEAN DEFAULT true,
    category VARCHAR, -- Added to match SQLAlchemy model
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Added to match SQLAlchemy model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RSS Items table
CREATE TABLE IF NOT EXISTS rss_items (
    id SERIAL PRIMARY KEY,
    feed_id INTEGER REFERENCES rss_feeds(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE, -- Changed from link to url to match SQLAlchemy model
    content TEXT, -- Added to match SQLAlchemy model
    summary TEXT, -- Added to match SQLAlchemy model
    author VARCHAR, -- Added to match SQLAlchemy model
    published_at TIMESTAMP,
    guid VARCHAR,
    tags JSONB DEFAULT '[]'::jsonb, -- Added to match SQLAlchemy model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(feed_id, guid)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(type);
CREATE INDEX IF NOT EXISTS idx_sources_created_at ON sources(created_at);
CREATE INDEX IF NOT EXISTS idx_highlights_source_id ON highlights(source_id);
CREATE INDEX IF NOT EXISTS idx_highlights_next_review ON highlights(next_review);
CREATE INDEX IF NOT EXISTS idx_highlights_tags ON highlights USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_embeddings_object_type ON embeddings(object_type);
CREATE INDEX IF NOT EXISTS idx_embeddings_object_id ON embeddings(object_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_url ON rss_feeds(url);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_active ON rss_feeds(is_active);
CREATE INDEX IF NOT EXISTS idx_rss_items_feed_id ON rss_items(feed_id);
CREATE INDEX IF NOT EXISTS idx_rss_items_published_at ON rss_items(published_at);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_sources_title_gin ON sources USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_highlights_text_gin ON highlights USING GIN(to_tsvector('english', text));
CREATE INDEX IF NOT EXISTS idx_highlights_note_gin ON highlights USING GIN(to_tsvector('english', note));

-- Insert some sample data
INSERT INTO sources (type, url, origin, title, author, summary) VALUES 
('web', 'https://example.com/article1', 'Example Site', 'Sample Article 1', 'John Doe', 'This is a sample article about knowledge management.'),
('web', 'https://example.com/article2', 'Example Site', 'Sample Article 2', 'Jane Smith', 'Another sample article about learning techniques.')
ON CONFLICT DO NOTHING;

INSERT INTO highlights (source_id, text, note, tags, summary, importance, difficulty) VALUES 
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

-- Reviews table (for spaced repetition)
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    highlight_id INTEGER REFERENCES highlights(id) ON DELETE CASCADE,
    next_review_at TIMESTAMP NOT NULL,
    interval_days INTEGER DEFAULT 1,
    ease_factor FLOAT DEFAULT 2.5,
    reps INTEGER DEFAULT 0,
    last_result INTEGER, -- 0-5 rating
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles table (for RSS items with full content)
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    feed_id INTEGER REFERENCES rss_feeds(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE,
    content TEXT,
    summary TEXT,
    author VARCHAR,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags JSONB DEFAULT '[]'::jsonb
);

-- Article embeddings table
CREATE TABLE IF NOT EXISTS article_embeddings (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    model VARCHAR(50) DEFAULT 'BAAI/bge-small-en-v1.5',
    vector VECTOR(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review sessions table (for tracking review performance)
CREATE TABLE IF NOT EXISTS review_sessions (
    id SERIAL PRIMARY KEY,
    highlight_id INTEGER REFERENCES highlights(id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL, -- 'quiz', 'flashcard', 'qa'
    question TEXT,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN,
    difficulty_rating INTEGER, -- 1-5
    time_spent INTEGER, -- seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exports table (for tracking export jobs)
CREATE TABLE IF NOT EXISTS exports (
    id SERIAL PRIMARY KEY,
    target VARCHAR(50) NOT NULL, -- 'obsidian', 'notion', etc.
    status VARCHAR(20) NOT NULL, -- 'pending', 'running', 'completed', 'failed'
    last_run_at TIMESTAMP,
    config_json TEXT, -- JSON configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create additional indexes for new tables
CREATE INDEX IF NOT EXISTS idx_reviews_highlight_id ON reviews(highlight_id);
CREATE INDEX IF NOT EXISTS idx_reviews_next_review_at ON reviews(next_review_at);
CREATE INDEX IF NOT EXISTS idx_articles_feed_id ON articles(feed_id);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_title_gin ON articles USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_articles_content_gin ON articles USING GIN(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_article_embeddings_article_id ON article_embeddings(article_id);
CREATE INDEX IF NOT EXISTS idx_article_embeddings_vector ON article_embeddings USING ivfflat (vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_review_sessions_highlight_id ON review_sessions(highlight_id);
CREATE INDEX IF NOT EXISTS idx_review_sessions_created_at ON review_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_exports_target ON exports(target);
CREATE INDEX IF NOT EXISTS idx_exports_status ON exports(status);

-- Create triggers for updated_at columns
CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exports_updated_at BEFORE UPDATE ON exports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for rss_feeds
CREATE TRIGGER update_rss_feeds_updated_at BEFORE UPDATE ON rss_feeds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

