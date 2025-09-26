"""
AI Processing Tasks
Handles AI summarization and tagging for articles
"""
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import Article
from app.services.ai import summarize_and_tag, is_ai_available

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Get database session"""
    return SessionLocal()


def run_ai_for_article(article_id):
    """
    Run AI processing for a specific article
    
    Args:
        article_id: ID of the article to process
    """
    if not is_ai_available():
        print("AI service not available - skipping AI processing")
        return
    
    db = get_session()
    try:
        article = db.query(Article).get(article_id)
        if not article:
            print(f"Article with ID {article_id} not found")
            return
        
        if not article.content_md:
            print(f"Article {article_id} has no markdown content - skipping AI processing")
            return
        
        print(f"Running AI processing for article: {article.title}")
        
        # Process with AI
        result = summarize_and_tag(article.content_md)
        
        # Update article with AI results
        if result.get("summary_bullets"):
            article.summary = "\n".join(result["summary_bullets"])
        
        if result.get("tags"):
            article.tags = result["tags"]
        
        db.commit()
        print(f"Successfully processed article: {article.title}")
        
    except Exception as e:
        print(f"Error in AI processing for article {article_id}: {e}")
        db.rollback()
    finally:
        db.close()


def run_ai_for_all_articles():
    """Run AI processing for all articles that haven't been processed yet"""
    if not is_ai_available():
        print("AI service not available - skipping AI processing")
        return
    
    db = get_session()
    try:
        # Find articles that have markdown content but no AI processing
        articles = db.query(Article).filter(
            Article.content_md.isnot(None),
            Article.summary.is_(None)
        ).all()
        
        print(f"Found {len(articles)} articles for AI processing")
        
        for article in articles:
            run_ai_for_article(article.id)
            
    except Exception as e:
        print(f"Error in run_ai_for_all_articles: {e}")
    finally:
        db.close()


def run_ai_for_article_batch(article_ids):
    """
    Run AI processing for a batch of articles
    
    Args:
        article_ids: List of article IDs to process
    """
    if not is_ai_available():
        print("AI service not available - skipping AI processing")
        return
    
    for article_id in article_ids:
        run_ai_for_article(article_id)