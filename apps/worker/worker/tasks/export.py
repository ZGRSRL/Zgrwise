"""
Export Tasks
Handles exporting digest and articles to various formats
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import Article

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Get database session"""
    return SessionLocal()


def export_markdown(filename: str, content: str, base_path: str = None) -> str:
    """
    Export content to markdown file
    
    Args:
        filename: Name of the file to create
        content: Markdown content to write
        base_path: Base directory path (defaults to OBSIDIAN_EXPORT_PATH)
        
    Returns:
        Path to the created file
    """
    if base_path is None:
        base_path = os.getenv("OBSIDIAN_EXPORT_PATH", "./data/exports")
    
    # Create base directory if it doesn't exist
    base_dir = Path(base_path)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file path
    file_path = base_dir / filename
    
    # Write content to file
    file_path.write_text(content, encoding="utf-8")
    
    print(f"Exported markdown to: {file_path}")
    return str(file_path)


def export_daily_digest(date: str = None) -> str:
    """
    Export daily digest to markdown
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        Path to the exported file
    """
    db = get_session()
    try:
        # Parse date or use today
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            target_date = datetime.now().date()
        
        # Calculate date range
        start_date = datetime.combine(target_date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        # Get articles for the date
        articles = db.query(Article).filter(
            Article.created_at >= start_date,
            Article.created_at < end_date,
            Article.is_read == False
        ).order_by(Article.priority.desc()).all()
        
        # Generate markdown content
        markdown = generate_digest_markdown(articles, target_date)
        
        # Create filename
        filename = f"daily-digest-{target_date.strftime('%Y-%m-%d')}.md"
        
        # Export to file
        file_path = export_markdown(filename, markdown)
        
        return file_path
        
    except Exception as e:
        print(f"Error exporting daily digest: {e}")
        return ""
    finally:
        db.close()


def generate_digest_markdown(articles: List[Article], date) -> str:
    """
    Generate markdown content for digest
    
    Args:
        articles: List of Article objects
        date: Date for the digest
        
    Returns:
        Markdown string
    """
    date_str = date.strftime("%Y-%m-%d")
    markdown = f"# ZgrWise – Daily Digest ({date_str})\n\n"
    
    if not articles:
        markdown += "No articles found for this date.\n"
        return markdown
    
    # Group by priority
    high_priority = [article for article in articles if article.priority >= 80]
    medium_priority = [article for article in articles if 50 <= article.priority < 80]
    low_priority = [article for article in articles if article.priority < 50]
    
    if high_priority:
        markdown += "## 🔥 High Priority\n\n"
        for article in high_priority:
            markdown += f"- [{article.title}]({article.url})"
            if article.summary:
                one_liner = article.summary.split("\n")[0]
                markdown += f" — {one_liner}"
            elif article.content_md:
                content = article.content_md.replace("\n", " ").strip()
                sentences = content.split(".")
                one_liner = sentences[0] + "." if sentences[0] else ""
                markdown += f" — {one_liner}"
            if article.source_domain:
                markdown += f" *({article.source_domain})*"
            markdown += "\n"
        markdown += "\n"
    
    if medium_priority:
        markdown += "## 📰 Medium Priority\n\n"
        for article in medium_priority:
            markdown += f"- [{article.title}]({article.url})"
            if article.summary:
                one_liner = article.summary.split("\n")[0]
                markdown += f" — {one_liner}"
            elif article.content_md:
                content = article.content_md.replace("\n", " ").strip()
                sentences = content.split(".")
                one_liner = sentences[0] + "." if sentences[0] else ""
                markdown += f" — {one_liner}"
            if article.source_domain:
                markdown += f" *({article.source_domain})*"
            markdown += "\n"
        markdown += "\n"
    
    if low_priority:
        markdown += "## 📚 Low Priority\n\n"
        for article in low_priority:
            markdown += f"- [{article.title}]({article.url})"
            if article.summary:
                one_liner = article.summary.split("\n")[0]
                markdown += f" — {one_liner}"
            elif article.content_md:
                content = article.content_md.replace("\n", " ").strip()
                sentences = content.split(".")
                one_liner = sentences[0] + "." if sentences[0] else ""
                markdown += f" — {one_liner}"
            if article.source_domain:
                markdown += f" *({article.source_domain})*"
            markdown += "\n"
    
    return markdown


def export_article_to_obsidian(article_id: int) -> str:
    """
    Export a single article to Obsidian format
    
    Args:
        article_id: ID of the article to export
        
    Returns:
        Path to the exported file
    """
    db = get_session()
    try:
        article = db.query(Article).get(article_id)
        if not article:
            print(f"Article with ID {article_id} not found")
            return ""
        
        # Generate Obsidian frontmatter
        frontmatter = f"""---
title: "{article.title}"
url: "{article.url}"
source_domain: "{article.source_domain or ''}"
priority: {article.priority}
published_at: "{article.published_at.isoformat() if article.published_at else ''}"
tags: {article.tags or []}
created_at: "{article.created_at.isoformat()}"
---

# {article.title}

**Source:** [{article.source_domain or 'Unknown'}]({article.url})
**Priority:** {article.priority}
**Published:** {article.published_at.strftime('%Y-%m-%d %H:%M') if article.published_at else 'Unknown'}

"""
        
        # Add summary if available
        if article.summary:
            frontmatter += f"## Summary\n\n{article.summary}\n\n"
        
        # Add content
        if article.content_md:
            frontmatter += f"## Content\n\n{article.content_md}"
        elif article.content:
            frontmatter += f"## Content\n\n{article.content}"
        
        # Create filename
        safe_title = "".join(c for c in article.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]  # Limit length
        filename = f"{safe_title}-{article.id}.md"
        
        # Export to file
        file_path = export_markdown(filename, frontmatter)
        
        return file_path
        
    except Exception as e:
        print(f"Error exporting article {article_id}: {e}")
        return ""
    finally:
        db.close()


def export_all_unread_articles() -> List[str]:
    """
    Export all unread articles to Obsidian format
    
    Returns:
        List of exported file paths
    """
    db = get_session()
    try:
        articles = db.query(Article).filter(
            Article.is_read == False
        ).order_by(Article.priority.desc()).all()
        
        exported_files = []
        for article in articles:
            file_path = export_article_to_obsidian(article.id)
            if file_path:
                exported_files.append(file_path)
        
        print(f"Exported {len(exported_files)} articles to Obsidian")
        return exported_files
        
    except Exception as e:
        print(f"Error exporting all unread articles: {e}")
        return []
    finally:
        db.close()