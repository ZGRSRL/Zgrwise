"""
Enhanced RSS feed processing tasks with AI integration
"""

import feedparser
import logging
import requests
from datetime import datetime
from typing import List, Dict, Any
from worker.utils.db import get_db_session
from worker.utils.models import Source, RSSFeed, Article
from worker.utils.ai import summarize_text, generate_tags
from worker.utils.embeddings import create_embedding

logger = logging.getLogger(__name__)


def fetch_all_rss_feeds():
    """Fetch and process all active RSS feeds"""
    try:
        with get_db_session() as db:
            feeds = db.query(RSSFeed).filter(RSSFeed.is_active == True).all()
            
            for feed in feeds:
                try:
                    process_rss_feed_enhanced(feed, db)
                    # Update last checked time
                    feed.last_checked = datetime.now()
                    db.commit()
                except Exception as e:
                    logger.error(f"Error processing feed {feed.url}: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error in fetch_all_rss_feeds: {e}")


def process_rss_feed_enhanced(feed: RSSFeed, db):
    """Process a single RSS feed with enhanced features"""
    logger.info(f"Processing RSS feed: {feed.url}")
    
    # Parse RSS feed
    parsed = feedparser.parse(feed.url)
    
    if parsed.bozo:
        logger.warning(f"RSS feed {feed.url} has parsing errors")
    
    # Process entries
    for entry in parsed.entries:
        try:
            process_rss_entry_enhanced(entry, feed, db)
        except Exception as e:
            logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
            continue


def process_rss_entry_enhanced(entry: Dict[str, Any], feed: RSSFeed, db):
    """Process a single RSS entry with AI enhancement"""
    # Check if article already exists
    existing = db.query(Article).filter(Article.url == entry.link).first()
    if existing:
        return
    
    # Extract content
    content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
    if not content:
        content = entry.get('summary', '')
    
    # Generate AI summary
    summary = None
    try:
        summary = summarize_text(content[:1000])  # Limit content length
    except Exception as e:
        logger.warning(f"Could not generate summary: {e}")
    
    # Generate AI tags
    tags = None
    try:
        tags_text = generate_tags(content[:1000])
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
    except Exception as e:
        logger.warning(f"Could not generate tags: {e}")
    
    # Create article
    article = Article(
        feed_id=feed.id,
        title=entry.get('title', 'Untitled'),
        url=entry.link,
        content=content,
        summary=summary,
        author=entry.get('author', ''),
        published_at=entry.get('published_parsed'),
        tags=tags or []
    )
    
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # Generate embedding for the article
    try:
        create_article_embedding(article, db)
    except Exception as e:
        logger.warning(f"Could not create embedding for article {article.id}: {e}")
    
    logger.info(f"Processed RSS entry: {article.title}")


def create_article_embedding(article: Article, db):
    """Create embedding for an article"""
    try:
        # Use title + summary + first 500 chars of content
        text_for_embedding = f"{article.title} {article.summary or ''} {article.content[:500]}"
        
        # Generate embedding
        embedding_vector = create_embedding(text_for_embedding)
        
        # Save to database (this would be implemented in the embeddings module)
        logger.info(f"Generated embedding for article {article.id}")
        
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")


def add_rss_feed_enhanced(url: str, title: str, category: str = "general"):
    """Add a new RSS feed with validation"""
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
            feed = RSSFeed(
                url=url,
                title=title,
                category=category,
                is_active=True
            )
            db.add(feed)
            db.commit()
            
            # Process the feed immediately
            process_rss_feed_enhanced(feed, db)
            
            return {"success": True, "feed_id": feed.id}
            
    except Exception as e:
        logger.error(f"Error adding RSS feed: {e}")
        return {"error": str(e)}


def refresh_specific_feed(feed_id: int):
    """Refresh a specific RSS feed"""
    try:
        with get_db_session() as db:
            feed = db.query(RSSFeed).filter(RSSFeed.id == feed_id).first()
            if not feed:
                return {"error": "Feed not found"}
            
            process_rss_feed_enhanced(feed, db)
            feed.last_checked = datetime.now()
            db.commit()
            
            return {"success": True, "message": "Feed refreshed successfully"}
            
    except Exception as e:
        logger.error(f"Error refreshing feed: {e}")
        return {"error": str(e)}


def get_feed_statistics():
    """Get RSS feed statistics"""
    try:
        with get_db_session() as db:
            total_feeds = db.query(RSSFeed).count()
            active_feeds = db.query(RSSFeed).filter(RSSFeed.is_active == True).count()
            total_articles = db.query(Article).count()
            
            # Get articles by category
            categories = db.query(RSSFeed.category, db.func.count(Article.id)).join(Article).group_by(RSSFeed.category).all()
            
            return {
                "total_feeds": total_feeds,
                "active_feeds": active_feeds,
                "total_articles": total_articles,
                "categories": dict(categories)
            }
            
    except Exception as e:
        logger.error(f"Error getting feed statistics: {e}")
        return {"error": str(e)} 