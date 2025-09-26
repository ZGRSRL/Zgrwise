"""
Daily Digest API Routes
Handles daily digest generation and export
"""
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import Article, RSSFeed

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter(prefix="/digest", tags=["digest"])


def get_session():
    """Get database session"""
    return SessionLocal()


@router.get("/daily")
def daily_digest(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    top: int = Query(10, description="Number of top articles to include"),
    unread_only: bool = Query(True, description="Include only unread articles")
):
    """
    Generate daily digest of articles
    
    Args:
        date: Specific date to generate digest for (defaults to today)
        top: Number of top articles to include
        unread_only: Whether to include only unread articles
        
    Returns:
        Dictionary with digest data and markdown
    """
    db = get_session()
    try:
        # Parse date or use today
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD"}
        else:
            target_date = datetime.now().date()
        
        # Calculate date range (last 24 hours)
        start_date = datetime.combine(target_date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        # Build query
        query = db.query(Article).filter(
            Article.created_at >= start_date,
            Article.created_at < end_date
        )
        
        if unread_only:
            query = query.filter(Article.is_read == False)
        
        # Order by priority and get top articles
        articles = query.order_by(Article.priority.desc()).limit(top).all()
        
        # Format articles for response
        items = []
        for article in articles:
            # Get one-liner summary
            one_liner = ""
            if article.summary:
                one_liner = article.summary.split("\n")[0]
            elif article.content_md:
                # Take first sentence from content
                content = article.content_md.replace("\n", " ").strip()
                sentences = content.split(".")
                one_liner = sentences[0] + "." if sentences[0] else ""
            
            items.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "one_liner": one_liner,
                "priority": article.priority,
                "source_domain": article.source_domain,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "tags": article.tags or []
            })
        
        # Generate markdown
        markdown = generate_digest_markdown(items, target_date)
        
        return {
            "date": target_date.isoformat(),
            "items": items,
            "markdown": markdown,
            "count": len(items)
        }
        
    except Exception as e:
        return {"error": f"Error generating digest: {str(e)}"}
    finally:
        db.close()


def generate_digest_markdown(items: List[Dict[str, Any]], date) -> str:
    """
    Generate markdown content for digest
    
    Args:
        items: List of article items
        date: Date for the digest
        
    Returns:
        Markdown string
    """
    date_str = date.strftime("%Y-%m-%d")
    markdown = f"# ZgrWise – Daily Digest ({date_str})\n\n"
    
    if not items:
        markdown += "No articles found for this date.\n"
        return markdown
    
    # Group by priority
    high_priority = [item for item in items if item.get("priority", 0) >= 80]
    medium_priority = [item for item in items if 50 <= item.get("priority", 0) < 80]
    low_priority = [item for item in items if item.get("priority", 0) < 50]
    
    if high_priority:
        markdown += "## 🔥 High Priority\n\n"
        for item in high_priority:
            markdown += f"- [{item['title']}]({item['url']})"
            if item['one_liner']:
                markdown += f" — {item['one_liner']}"
            if item['source_domain']:
                markdown += f" *({item['source_domain']})*"
            markdown += "\n"
        markdown += "\n"
    
    if medium_priority:
        markdown += "## 📰 Medium Priority\n\n"
        for item in medium_priority:
            markdown += f"- [{item['title']}]({item['url']})"
            if item['one_liner']:
                markdown += f" — {item['one_liner']}"
            if item['source_domain']:
                markdown += f" *({item['source_domain']})*"
            markdown += "\n"
        markdown += "\n"
    
    if low_priority:
        markdown += "## 📚 Low Priority\n\n"
        for item in low_priority:
            markdown += f"- [{item['title']}]({item['url']})"
            if item['one_liner']:
                markdown += f" — {item['one_liner']}"
            if item['source_domain']:
                markdown += f" *({item['source_domain']})*"
            markdown += "\n"
    
    return markdown


@router.get("/stats")
def digest_stats():
    """
    Get digest statistics
    
    Returns:
        Dictionary with digest statistics
    """
    db = get_session()
    try:
        # Get today's stats
        today = datetime.now().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        total_articles = db.query(Article).filter(
            Article.created_at >= start_date,
            Article.created_at < end_date
        ).count()
        
        unread_articles = db.query(Article).filter(
            Article.created_at >= start_date,
            Article.created_at < end_date,
            Article.is_read == False
        ).count()
        
        high_priority = db.query(Article).filter(
            Article.created_at >= start_date,
            Article.created_at < end_date,
            Article.priority >= 80
        ).count()
        
        return {
            "date": today.isoformat(),
            "total_articles": total_articles,
            "unread_articles": unread_articles,
            "high_priority_articles": high_priority,
            "read_percentage": round((total_articles - unread_articles) / total_articles * 100, 1) if total_articles > 0 else 0
        }
        
    except Exception as e:
        return {"error": f"Error getting stats: {str(e)}"}
    finally:
        db.close()