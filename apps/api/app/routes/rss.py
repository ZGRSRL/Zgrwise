from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import feedparser
import requests
from ..db import get_db
from ..models import RSSFeed, Article, ArticleEmbedding
from ..schemas import RSSFeedCreate, RSSFeedResponse, ArticleResponse
from ..logic.ai import generate_summary, generate_tags
from ..logic.embeddings import create_embedding

router = APIRouter()


@router.post("/rss/feeds", response_model=RSSFeedResponse)
async def create_rss_feed(feed: RSSFeedCreate, db: Session = Depends(get_db)):
    """Add a new RSS feed"""
    # Check if feed already exists
    existing = db.query(RSSFeed).filter(RSSFeed.url == feed.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feed already exists")
    
    # Test the feed
    try:
        parsed = feedparser.parse(feed.url)
        if parsed.bozo:
            raise HTTPException(status_code=400, detail="Invalid RSS feed")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not fetch RSS feed")
    
    # Create feed
    db_feed = RSSFeed(
        url=feed.url,
        title=feed.title,
        category=feed.category or "general"
    )
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    
    return db_feed


@router.get("/rss/feeds", response_model=List[RSSFeedResponse])
async def get_rss_feeds(db: Session = Depends(get_db)):
    """Get all RSS feeds"""
    feeds = db.query(RSSFeed).filter(RSSFeed.is_active == True).all()
    return feeds


@router.post("/rss/feeds/{feed_id}/refresh")
async def refresh_rss_feed(
    feed_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Refresh a specific RSS feed and process new articles"""
    feed = db.query(RSSFeed).filter(RSSFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    # Update last checked time
    feed.last_checked = datetime.now()
    db.commit()
    
    # Process feed in background
    background_tasks.add_task(process_rss_feed, feed_id)
    
    return {"message": "Feed refresh started"}


@router.get("/rss/articles", response_model=List[ArticleResponse])
async def get_articles(
    feed_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get articles, optionally filtered by feed_id"""
    query = db.query(Article)
    
    if feed_id:
        query = query.filter(Article.feed_id == feed_id)
    
    articles = query.order_by(Article.published_at.desc()).limit(limit).all()
    return articles


async def process_rss_feed(feed_id: int):
    """Process RSS feed and extract articles"""
    # This would run in background
    # Implementation in worker service
    pass 