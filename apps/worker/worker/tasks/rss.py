"""
RSS feed processing tasks
"""

import feedparser
import logging
from datetime import datetime
from typing import List, Dict, Any
import requests
from worker.utils.db import get_db_session
from worker.utils.models import Source, RSSFeed
from worker.utils.ai import summarize_text, generate_tags

logger = logging.getLogger(__name__)


def fetch_rss_feeds():
    """Fetch all RSS feeds and process new entries"""
    try:
        with get_db_session() as db:
            feeds = db.query(RSSFeed).all()
            
            for feed in feeds:
                try:
                    process_rss_feed(feed, db)
                    # Update last checked time
                    feed.last_checked = datetime.now()
                    db.commit()
                except Exception as e:
                    logger.error(f"Error processing feed {feed.url}: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error in fetch_rss_feeds: {e}")


def process_rss_feed(feed: RSSFeed, db):
    """Process a single RSS feed"""
    logger.info(f"Processing RSS feed: {feed.url}")
    
    # Parse RSS feed
    parsed = feedparser.parse(feed.url)
    
    if parsed.bozo:
        logger.warning(f"RSS feed {feed.url} has parsing errors")
    
    # Process entries
    for entry in parsed.entries:
        try:
            process_rss_entry(entry, feed, db)
        except Exception as e:
            logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
            continue


def process_rss_entry(entry: Dict[str, Any], feed: RSSFeed, db):
    """Process a single RSS entry"""
    # Check if source already exists
    existing = db.query(Source).filter(Source.url == entry.link).first()
    if existing:
        return
    
    # Extract content
    content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
    if not content:
        content = entry.get('summary', '')
    
    # Create source
    source = Source(
        type='rss',
        url=entry.link,
        origin=feed.title,
        title=entry.get('title', 'Untitled'),
        author=entry.get('author', ''),
        created_at=datetime.now(),
        raw=content
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    # Generate AI summary and tags
    try:
        summary = summarize_text(content[:1000])  # Limit content length
        source.summary = summary
        db.commit()
    except Exception as e:
        logger.warning(f"Could not generate summary for {source.id}: {e}")
    
    logger.info(f"Processed RSS entry: {source.title}")


def add_rss_feed(url: str, title: str):
    """Add a new RSS feed"""
    try:
        with get_db_session() as db:
            # Check if feed already exists
            existing = db.query(RSSFeed).filter(RSSFeed.url == url).first()
            if existing:
                return {"error": "Feed already exists"}
            
            # Test the feed
            parsed = feedparser.parse(url)
            if parsed.bozo:
                return {"error": "Invalid RSS feed"}
            
            # Add feed
            feed = RSSFeed(url=url, title=title)
            db.add(feed)
            db.commit()
            
            return {"success": True, "feed_id": feed.id}
            
    except Exception as e:
        logger.error(f"Error adding RSS feed: {e}")
        return {"error": str(e)} 