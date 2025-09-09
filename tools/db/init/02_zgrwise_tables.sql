-- ZgrWise Database Tables for Feed database
-- Run this script in your Feed database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Create enum types
CREATE TYPE source_type AS ENUM ('web', 'pdf', 'youtube', 'rss', 'kindle', 'newsletter');

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    type source_type NOT NULL,
    url TEXT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw TEXT,
    summary TEXT
);

-- Highlights table
CREATE TABLE IF NOT EXISTS highlights (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    note TEXT,
    location VARCHAR(255),
    color VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL, -- 'source' or 'highlight'
    object_id INTEGER NOT NULL,
    model VARCHAR(100) NOT NULL,
    vector vector(384) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table (Spaced Repetition)
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    highlight_id INTEGER NOT NULL REFERENCES highlights(id) ON DELETE CASCADE,
    next_review_at TIMESTAMP NOT NULL,
    interval INTEGER DEFAULT 1, -- days
    ease FLOAT DEFAULT 2.5,
    reps INTEGER DEFAULT 0,
    last_result INTEGER, -- 0-5
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RSS Feeds table
CREATE TABLE IF NOT EXISTS rss_feeds (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    category VARCHAR(100) DEFAULT 'general'
);

-- Articles table (from RSS feeds)
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    feed_id INTEGER NOT NULL REFERENCES rss_feeds(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    summary TEXT,
    author VARCHAR(255),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags JSONB -- Store tags as JSON array
);

-- Article Embeddings table
CREATE TABLE IF NOT EXISTS article_embeddings (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    model VARCHAR(100) NOT NULL,
    vector vector(384) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review Sessions table (for learning analytics)
CREATE TABLE IF NOT EXISTS review_sessions (
    id SERIAL PRIMARY KEY,
    highlight_id INTEGER NOT NULL REFERENCES highlights(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'quiz', 'flashcard', 'qa'
    question TEXT,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN,
    difficulty_rating INTEGER, -- 1-5
    time_spent INTEGER, -- seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exports table
CREATE TABLE IF NOT EXISTS exports (
    id SERIAL PRIMARY KEY,
    target VARCHAR(100) NOT NULL, -- 'obsidian'
    status VARCHAR(100) NOT NULL,
    last_run_at TIMESTAMP,
    config_json TEXT -- JSON string
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sources_title_gin ON sources USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sources_raw_gin ON sources USING gin (raw gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_highlights_text_gin ON highlights USING gin (text gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (vector vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_reviews_next_review ON reviews (next_review_at);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles (published_at);
CREATE INDEX IF NOT EXISTS idx_articles_title_gin ON articles USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_articles_content_gin ON articles USING gin (content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_article_embeddings_vector ON article_embeddings USING ivfflat (vector vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_review_sessions_highlight ON review_sessions (highlight_id);
CREATE INDEX IF NOT EXISTS idx_review_sessions_created ON review_sessions (created_at);

-- Insert sample data for testing
INSERT INTO rss_feeds (url, title, category) VALUES 
('https://feeds.feedburner.com/TechCrunch', 'TechCrunch', 'tech'),
('https://rss.cnn.com/rss/edition.rss', 'CNN News', 'news')
ON CONFLICT (url) DO NOTHING;

-- Create a sample source and highlight for testing
INSERT INTO sources (type, url, origin, title, author, summary) VALUES 
('web', 'https://example.com/sample', 'Manual Entry', 'Sample Article', 'John Doe', 'This is a sample article for testing purposes.')
ON CONFLICT DO NOTHING;

-- Get the source ID and create a highlight
DO $$
DECLARE
    source_id INTEGER;
BEGIN
    SELECT id INTO source_id FROM sources WHERE url = 'https://example.com/sample' LIMIT 1;
    IF source_id IS NOT NULL THEN
        INSERT INTO highlights (source_id, text, note) VALUES 
        (source_id, 'This is a sample highlight text for testing the system.', 'Test note')
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- Display created tables
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name; 