from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from .db import Base

class RSSFeed(Base):
    __tablename__ = "rss_feeds"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    etag = Column(String, nullable=True)
    last_modified = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class RSSItem(Base):
    __tablename__ = "rss_items"
    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("rss_feeds.id", ondelete="CASCADE"), index=True, nullable=False)
    guid_hash = Column(String, nullable=False)   # md5(guid||link)
    link = Column(String, nullable=False)
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    summary_html = Column(Text, nullable=True)
    content_text = Column(Text, nullable=True)   # trafilatura ile çıkarılan gövde
    tags = Column(JSONB, nullable=True)          # auto-tag sonuçları
    vectors_ok = Column(Boolean, default=False)
    status = Column(String, default="new")       # new -> processed -> indexed
    raw = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('feed_id','guid_hash', name='uq_rssitem_feed_guid'),
        Index('ix_rssitem_published', 'published_at'),
    )