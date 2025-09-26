"""
Content Normalization Tasks
Converts HTML content to Markdown format
"""
import trafilatura
import time
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import Article

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Get database session"""
    return SessionLocal()


def normalize_article(article_id):
    """
    Normalize article content from HTML to Markdown
    
    Args:
        article_id: ID of the article to normalize
    """
    db = get_session()
    try:
        article = db.query(Article).get(article_id)
        if not article:
            print(f"Article with ID {article_id} not found")
            return
        
        if not article.url:
            print(f"Article {article_id} has no URL")
            return
        
        print(f"Normalizing article: {article.title}")
        
        # Fetch and extract content
        try:
            html = trafilatura.fetch_url(article.url)
            if not html:
                print(f"Could not fetch content from {article.url}")
                return
            
            # Extract markdown content
            md_content = trafilatura.extract(html, output="markdown")
            if not md_content:
                print(f"Could not extract markdown from {article.url}")
                return
            
            # Update article with markdown content
            article.content_md = md_content.strip()
            
            # Also update the raw content if it's empty
            if not article.content:
                article.content = trafilatura.extract(html, output="text")
            
            db.commit()
            print(f"Successfully normalized article: {article.title}")
            
        except Exception as e:
            print(f"Error normalizing article {article.title}: {e}")
            return
        
        # Small delay to be respectful to servers
        time.sleep(1)
        
    except Exception as e:
        print(f"Error in normalize_article: {e}")
        db.rollback()
    finally:
        db.close()


def normalize_all_articles():
    """Normalize all articles that don't have markdown content yet"""
    db = get_session()
    try:
        articles = db.query(Article).filter(
            Article.content_md.is_(None),
            Article.url.isnot(None)
        ).all()
        
        print(f"Found {len(articles)} articles to normalize")
        
        for article in articles:
            normalize_article(article.id)
            
    except Exception as e:
        print(f"Error in normalize_all_articles: {e}")
    finally:
        db.close()


def normalize_article_batch(article_ids):
    """
    Normalize a batch of articles
    
    Args:
        article_ids: List of article IDs to normalize
    """
    for article_id in article_ids:
        normalize_article(article_id)