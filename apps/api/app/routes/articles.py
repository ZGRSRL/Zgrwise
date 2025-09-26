"""
Articles API Routes
Handles article listing and management
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc
from app.db import engine
from app.models import Article

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter(prefix="/articles", tags=["articles"])


def get_session():
    """Get database session"""
    return SessionLocal()


@router.get("/")
def list_articles(
    filter_type: str = Query("unread", description="Filter type: all, unread, read, high_priority"),
    sort: str = Query("priority", description="Sort by: priority, date, title"),
    limit: int = Query(50, description="Number of articles to return"),
    offset: int = Query(0, description="Number of articles to skip")
):
    """
    List articles with filtering and sorting
    
    Args:
        filter_type: Type of filter to apply
        sort: Field to sort by
        limit: Maximum number of articles to return
        offset: Number of articles to skip
        
    Returns:
        List of articles with metadata
    """
    db = get_session()
    try:
        # Build base query
        query = db.query(Article)
        
        # Apply filters
        if filter_type == "unread":
            query = query.filter(Article.is_read == False)
        elif filter_type == "read":
            query = query.filter(Article.is_read == True)
        elif filter_type == "high_priority":
            query = query.filter(Article.priority >= 80)
        # "all" doesn't add any filter
        
        # Apply sorting
        if sort == "priority":
            query = query.order_by(desc(Article.priority), desc(Article.created_at))
        elif sort == "date":
            query = query.order_by(desc(Article.created_at))
        elif sort == "title":
            query = query.order_by(asc(Article.title))
        else:
            query = query.order_by(desc(Article.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        articles = query.offset(offset).limit(limit).all()
        
        # Format response
        items = []
        for article in articles:
            # Get one-liner summary
            one_liner = ""
            if article.summary:
                one_liner = article.summary.split("\n")[0]
            elif article.content_md:
                content = article.content_md.replace("\n", " ").strip()
                sentences = content.split(".")
                one_liner = sentences[0] + "." if sentences[0] else ""
            
            items.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "one_liner": one_liner,
                "priority": article.priority,
                "is_read": article.is_read,
                "source_domain": article.source_domain,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "created_at": article.created_at.isoformat(),
                "tags": article.tags or []
            })
        
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing articles: {str(e)}")
    finally:
        db.close()


@router.post("/{article_id}/read")
def toggle_read(article_id: int, value: bool):
    """
    Toggle read status of an article
    
    Args:
        article_id: ID of the article
        value: True to mark as read, False to mark as unread
        
    Returns:
        Success message
    """
    db = get_session()
    try:
        article = db.query(Article).get(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article.is_read = value
        db.commit()
        
        return {"message": f"Article marked as {'read' if value else 'unread'}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating article: {str(e)}")
    finally:
        db.close()


@router.get("/{article_id}")
def get_article(article_id: int):
    """
    Get detailed information about a specific article
    
    Args:
        article_id: ID of the article
        
    Returns:
        Detailed article information
    """
    db = get_session()
    try:
        article = db.query(Article).get(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "content": article.content,
            "content_md": article.content_md,
            "summary": article.summary,
            "author": article.author,
            "priority": article.priority,
            "is_read": article.is_read,
            "source_domain": article.source_domain,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "created_at": article.created_at.isoformat(),
            "tags": article.tags or [],
            "feed": {
                "id": article.feed.id,
                "title": article.feed.title,
                "url": article.feed.url
            } if article.feed else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting article: {str(e)}")
    finally:
        db.close()


@router.get("/stats/overview")
def get_article_stats():
    """
    Get overview statistics for articles
    
    Returns:
        Statistics about articles
    """
    db = get_session()
    try:
        total = db.query(Article).count()
        unread = db.query(Article).filter(Article.is_read == False).count()
        high_priority = db.query(Article).filter(Article.priority >= 80).count()
        read_percentage = round((total - unread) / total * 100, 1) if total > 0 else 0
        
        return {
            "total_articles": total,
            "unread_articles": unread,
            "read_articles": total - unread,
            "high_priority_articles": high_priority,
            "read_percentage": read_percentage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
    finally:
        db.close()