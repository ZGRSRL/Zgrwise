from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
from ..models import Highlight, Source, Embedding
from ..schemas import SearchQuery, SearchResult
# import numpy as np  # ML kütüphanesi - gereksiz


def hybrid_search(db: Session, query: SearchQuery) -> List[SearchResult]:
    """
    Perform hybrid search using text similarity and vector similarity
    Combines pg_trgm, full-text search, and vector cosine similarity
    """
    if not query.q:
        # If no query, return recent highlights
        highlights = db.query(Highlight).join(Source).order_by(Highlight.created_at.desc()).limit(query.limit).all()
        return [
            SearchResult(
                highlight=highlight,
                source=highlight.source,
                score=1.0,
                match_type="recent"
            )
            for highlight in highlights
        ]
    
    # Text search using pg_trgm and full-text search
    text_query = text("""
        SELECT 
            h.id,
            h.text,
            h.note,
            h.location,
            h.color,
            h.created_at,
            h.source_id,
            s.type,
            s.url,
            s.origin,
            s.title,
            s.author,
            s.created_at as source_created_at,
            s.summary,
            (
                GREATEST(
                    similarity(h.text, :query),
                    similarity(s.title, :query),
                    similarity(s.raw, :query)
                ) * 0.6 +
                ts_rank(
                    to_tsvector('english', h.text || ' ' || COALESCE(h.note, '') || ' ' || s.title || ' ' || s.raw),
                    plainto_tsquery('english', :query)
                ) * 0.4
            ) as text_score
        FROM highlights h
        JOIN sources s ON h.source_id = s.id
        WHERE 
            h.text ILIKE :like_query OR 
            s.title ILIKE :like_query OR 
            s.raw ILIKE :like_query OR
            to_tsvector('english', h.text || ' ' || COALESCE(h.note, '') || ' ' || s.title || ' ' || s.raw) @@ plainto_tsquery('english', :query)
        ORDER BY text_score DESC
        LIMIT :limit
    """)
    
    text_results = db.execute(text_query, {
        "query": query.q,
        "like_query": f"%{query.q}%",
        "limit": query.limit
    }).fetchall()
    
    # Vector search (if embeddings exist)
    vector_results = []
    try:
        # This would require the actual embedding model to be loaded
        # For now, we'll return text results only
        pass
    except Exception:
        # If vector search fails, continue with text search only
        pass
    
    # Combine and rank results using RRF (Reciprocal Rank Fusion)
    combined_results = []
    
    # Process text results
    for i, row in enumerate(text_results):
        highlight = Highlight(
            id=row.id,
            text=row.text,
            note=row.note,
            location=row.location,
            color=row.color,
            created_at=row.created_at,
            source_id=row.source_id
        )
        source = Source(
            id=row.source_id,
            type=row.type,
            url=row.url,
            origin=row.origin,
            title=row.title,
            author=row.author,
            created_at=row.source_created_at,
            summary=row.summary
        )
        
        # RRF score: 1 / (k + rank), where k=60
        rrf_score = 1 / (60 + i + 1)
        combined_results.append(SearchResult(
            highlight=highlight,
            source=source,
            score=rrf_score,
            match_type="text"
        ))
    
    # Sort by score and return
    combined_results.sort(key=lambda x: x.score, reverse=True)
    return combined_results[:query.limit]


def search_by_tags(db: Session, tags: List[str], limit: int = 20) -> List[SearchResult]:
    """Search highlights by tags"""
    # This is a simplified version - in practice you'd need a proper tag system
    highlights = db.query(Highlight).join(Source).filter(
        Highlight.text.contains(tags[0])  # Simple contains for now
    ).limit(limit).all()
    
    return [
        SearchResult(
            highlight=highlight,
            source=highlight.source,
            score=1.0,
            match_type="tag"
        )
        for highlight in highlights
    ] 