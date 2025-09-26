"""
RSS Feed Pulling Tasks
Handles RSS feed fetching and article creation
"""
from datetime import datetime
import feedparser
import tldextract
import hashlib
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import RSSFeed, Article

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Get database session"""
    return SessionLocal()


def article_guid(entry):
    """Generate unique GUID for article based on entry data"""
    raw = (entry.get('id') or entry.get('link') or '') + (entry.get('title') or '')
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def pull_feed(feed_id=None):
    """
    Pull RSS feed and create new articles
    
    Args:
        feed_id: Specific feed ID to pull, or None for all feeds
    """
    db = get_session()
    try:
        # Get feeds to process
        if feed_id:
            feeds = [db.query(RSSFeed).get(feed_id)]
            if not feeds[0]:
                print(f"Feed with ID {feed_id} not found")
                return
        else:
            feeds = db.query(RSSFeed).filter(RSSFeed.is_active == True).all()
        
        print(f"Processing {len(feeds)} RSS feeds...")
        
        for feed in feeds:
            try:
                print(f"Processing feed: {feed.title} ({feed.url})")
                
                # Parse RSS feed
                parsed = feedparser.parse(feed.url)
                
                if parsed.bozo:
                    print(f"Warning: Feed {feed.title} has parsing issues")
                
                new_articles = 0
                
                for entry in parsed.entries:
                    try:
                        # Generate unique GUID
                        guid = article_guid(entry)
                        
                        # Check if article already exists
                        existing = db.query(Article).filter_by(guid=guid).first()
                        if existing:
                            continue
                        
                        # Extract domain
                        domain = None
                        if entry.get('link'):
                            domain = tldextract.extract(entry.link).registered_domain
                        
                        # Parse published date
                        published_at = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])
                        
                        # Create new article
                        article = Article(
                            feed_id=feed.id,
                            title=entry.get('title', '(untitled)'),
                            url=entry.get('link', ''),
                            content=entry.get('description', ''),
                            author=entry.get('author', ''),
                            published_at=published_at,
                            priority=feed.weight or 50,
                            source_domain=domain,
                            guid=guid,
                            is_read=False
                        )
                        
                        db.add(article)
                        new_articles += 1
                        
                    except Exception as e:
                        print(f"Error processing entry: {e}")
                        continue
                
                # Update last_checked timestamp
                feed.last_checked = datetime.utcnow()
                
                print(f"Added {new_articles} new articles from {feed.title}")
                
            except Exception as e:
                print(f"Error processing feed {feed.title}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print("RSS pull completed successfully")
        
    except Exception as e:
        print(f"Error in RSS pull: {e}")
        db.rollback()
    finally:
        db.close()


def pull_all_feeds():
    """Pull all active RSS feeds"""
    pull_feed()


def pull_single_feed(feed_id):
    """Pull a specific RSS feed by ID"""
    pull_feed(feed_id)