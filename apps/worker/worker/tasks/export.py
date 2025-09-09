"""
Export tasks for Obsidian and other formats
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, List
from worker.utils.db import get_db_session
from worker.utils.models import Source, Highlight

logger = logging.getLogger(__name__)

EXPORT_PATH = os.getenv('OBSIDIAN_EXPORT_PATH', './data/exports')


def export_to_obsidian() -> Dict[str, Any]:
    """Export highlights to Obsidian format"""
    try:
        # Ensure export directory exists
        os.makedirs(EXPORT_PATH, exist_ok=True)
        
        with get_db_session() as db:
            # Get all highlights with sources
            highlights = db.query(Highlight).join(Source).all()
            
            exported_count = 0
            for highlight in highlights:
                try:
                    content = generate_obsidian_content(highlight)
                    filename = f"{highlight.id}_{highlight.text[:50].replace(' ', '_')}.md"
                    filepath = os.path.join(EXPORT_PATH, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    exported_count += 1
                    
                except Exception as e:
                    logger.error(f"Error exporting highlight {highlight.id}: {e}")
                    continue
            
            logger.info(f"Exported {exported_count} highlights to Obsidian")
            return {"status": "success", "exported_count": exported_count}
            
    except Exception as e:
        logger.error(f"Error in Obsidian export: {e}")
        return {"status": "error", "message": str(e)}


def generate_obsidian_content(highlight: Highlight) -> str:
    """Generate Obsidian markdown content for a highlight"""
    source = highlight.source
    
    # Create frontmatter
    frontmatter = f"""---
title: "{source.title}"
source_url: "{source.url}"
source_type: "{source.type}"
origin: "{source.origin}"
author: "{source.author or 'Unknown'}"
created: "{source.created_at}"
tags: [{', '.join(source.tags) if source.tags else ''}]
summary: "{source.summary or ''}"
---

# Highlights

> {highlight.text}

- note: {highlight.note or ''}
- added: {highlight.created_at}
- location: {highlight.location or ''}

## Source Details

**Title:** {source.title}
**URL:** {source.url}
**Type:** {source.type}
**Origin:** {source.origin}
**Author:** {source.author or 'Unknown'}
**Created:** {source.created_at}

"""
    
    if source.summary:
        frontmatter += f"**Summary:** {source.summary}\n\n"
    
    if source.raw:
        frontmatter += f"**Content:**\n\n{source.raw}\n"
    
    return frontmatter


def export_to_markdown(highlight_ids: List[int] = None) -> Dict[str, Any]:
    """Export specific highlights to markdown"""
    try:
        with get_db_session() as db:
            if highlight_ids:
                highlights = db.query(Highlight).filter(Highlight.id.in_(highlight_ids)).join(Source).all()
            else:
                highlights = db.query(Highlight).join(Source).all()
            
            # Generate markdown content
            content = "# ZgrWise Highlights\n\n"
            
            for highlight in highlights:
                content += f"## {highlight.source.title}\n\n"
                content += f"> {highlight.text}\n\n"
                content += f"- Source: {highlight.source.url}\n"
                content += f"- Added: {highlight.created_at}\n\n"
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"highlights_{timestamp}.md"
            filepath = os.path.join(EXPORT_PATH, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Exported {len(highlights)} highlights to {filename}")
            return {"status": "success", "filename": filename, "exported_count": len(highlights)}
            
    except Exception as e:
        logger.error(f"Error in markdown export: {e}")
        return {"status": "error", "message": str(e)} 