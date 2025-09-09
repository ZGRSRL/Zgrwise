"""
Database models for worker
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, Index, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# For pgvector support - we'll use a custom type
from sqlalchemy import TypeDecorator, String
import json

class VECTOR(TypeDecorator):
    impl = String
    cache_ok = True
    
    def __init__(self, dimensions=384):
        self.dimensions = dimensions
        super().__init__()
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, list):
                return json.dumps(value)
            return value
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, str):
                return json.loads(value)
            return value
        return None


class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    raw = Column(Text)
    summary = Column(Text)
    
    # Relationships
    highlights = relationship("Highlight", back_populates="source")
    embedding = relationship("Embedding", back_populates="source", uselist=False)


class Highlight(Base):
    __tablename__ = "highlights"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    text = Column(Text, nullable=False)
    note = Column(Text)
    location = Column(String)
    color = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source = relationship("Source", back_populates="highlights")
    embedding = relationship("Embedding", back_populates="highlight", uselist=False)
    reviews = relationship("Review", back_populates="highlight")


class Embedding(Base):
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    object_type = Column(String, nullable=False)  # 'source' or 'highlight'
    object_id = Column(Integer, nullable=False)
    model = Column(String, nullable=False)
    vector = Column(VECTOR(384), nullable=False)
    
    # Relationships
    source = relationship("Source", back_populates="embedding", foreign_keys=[object_id])
    highlight = relationship("Highlight", back_populates="embedding", foreign_keys=[object_id])


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    highlight_id = Column(Integer, ForeignKey("highlights.id"), nullable=False)
    next_review_at = Column(DateTime, nullable=False)
    interval = Column(Integer, default=1)  # days
    ease = Column(Float, default=2.5)
    reps = Column(Integer, default=0)
    last_result = Column(Integer)  # 0-5
    
    # Relationships
    highlight = relationship("Highlight", back_populates="reviews")


class RSSFeed(Base):
    __tablename__ = "rss_feeds"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime)
    is_active = Column(Boolean, default=True)
    category = Column(String)  # 'blog', 'news', 'research', etc.


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("rss_feeds.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    author = Column(String)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON)  # Store tags as JSON array
    
    # Relationships
    feed = relationship("RSSFeed")
    embedding = relationship("ArticleEmbedding", back_populates="article", uselist=False)


class ArticleEmbedding(Base):
    __tablename__ = "article_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    model = Column(String, nullable=False)
    vector = Column(VECTOR(384), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="embedding")