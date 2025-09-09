"""
Enhanced hybrid search combining text similarity, vector embeddings, and RRF fusion
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from ..models import Highlight, Source, Article, ArticleEmbedding
from ..schemas import SearchQuery, SearchResult
import numpy as np
import logging

logger = logging.getLogger(__name__)


def hybrid_search_enhanced(db: Session, query: SearchQuery) -> List[SearchResult]:
    """
    Enhanced hybrid search using:
    1. Text similarity (pg_trgm + full-text search)
    2. Vector similarity (cosine distance)
    3. RRF fusion for result ranking
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
    
    # 1. Text Search (pg_trgm + full-text)
    text_results = perform_text_search(db, query)
    
    # 2. Vector Search (embeddings)
    vector_results = perform_vector_search(db, query)
    
    # 3. Combine results using RRF
    combined_results = combine_results_rrf(text_results, vector_results, query.limit)
    
    return combined_results


def perform_text_search(db: Session, query: SearchQuery) -> List[Dict[str, Any]]:
    """Perform text-based search using pg_trgm and full-text search"""
    try:
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
                        COALESCE(similarity(s.raw, :query), 0)
                    ) * 0.6 +
                    ts_rank(
                        to_tsvector('english', h.text || ' ' || COALESCE(h.note, '') || ' ' || s.title || ' ' || COALESCE(s.raw, '')),
                        plainto_tsquery('english', :query)
                    ) * 0.4
                ) as text_score
            FROM highlights h
            JOIN sources s ON h.source_id = s.id
            WHERE 
                h.text ILIKE :like_query OR 
                s.title ILIKE :like_query OR 
                COALESCE(s.raw, '') ILIKE :like_query OR
                to_tsvector('english', h.text || ' ' || COALESCE(h.note, '') || ' ' || s.title || ' ' || COALESCE(s.raw, '')) @@ plainto_tsquery('english', :query)
            ORDER BY text_score DESC
            LIMIT :limit
        """)
        
        results = db.execute(text_query, {
            "query": query.q,
            "like_query": f"%{query.q}%",
            "limit": query.limit * 2  # Get more for better fusion
        }).fetchall()
        
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Error in text search: {e}")
        return []


def perform_vector_search(db: Session, query: SearchQuery) -> List[Dict[str, Any]]:
    """Perform vector-based search using embeddings"""
    try:
        # For now, return empty results as embeddings need to be implemented
        # This would involve:
        # 1. Generating query embedding
        # 2. Using pgvector for similarity search
        # 3. Returning results with cosine similarity scores
        
        logger.info("Vector search not yet implemented - returning empty results")
        return []
        
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        return []


def combine_results_rrf(text_results: List[Dict], vector_results: List[Dict], limit: int) -> List[SearchResult]:
    """Combine results using Reciprocal Rank Fusion (RRF)"""
    try:
        # Create result mapping
        result_map = {}
        
        # Process text results
        for i, result in enumerate(text_results):
            highlight_id = result['id']
            if highlight_id not in result_map:
                result_map[highlight_id] = {
                    'highlight_data': result,
                    'text_rank': i + 1,
                    'vector_rank': None,
                    'text_score': result.get('text_score', 0)
                }
        
        # Process vector results
        for i, result in enumerate(vector_results):
            highlight_id = result['id']
            if highlight_id in result_map:
                result_map[highlight_id]['vector_rank'] = i + 1
            else:
                result_map[highlight_id] = {
                    'highlight_data': result,
                    'text_rank': None,
                    'vector_rank': i + 1,
                    'text_score': 0
                }
        
        # Calculate RRF scores
        k = 60  # RRF constant
        for highlight_id, data in result_map.items():
            text_rrf = 1 / (k + data['text_rank']) if data['text_rank'] else 0
            vector_rrf = 1 / (k + data['vector_rank']) if data['vector_rank'] else 0
            
            # Combine scores (you can adjust weights)
            data['final_score'] = text_rrf * 0.7 + vector_rrf * 0.3
        
        # Sort by final score and convert to SearchResult objects
        sorted_results = sorted(result_map.values(), key=lambda x: x['final_score'], reverse=True)
        
        # Convert to SearchResult objects
        search_results = []
        for data in sorted_results[:limit]:
            highlight_data = data['highlight_data']
            
            # Create Highlight object
            highlight = Highlight(
                id=highlight_data['id'],
                text=highlight_data['text'],
                note=highlight_data['note'],
                location=highlight_data['location'],
                color=highlight_data['color'],
                created_at=highlight_data['created_at'],
                source_id=highlight_data['source_id']
            )
            
            # Create Source object
            source = Source(
                id=highlight_data['source_id'],
                type=highlight_data['type'],
                url=highlight_data['url'],
                origin=highlight_data['origin'],
                title=highlight_data['title'],
                author=highlight_data['author'],
                created_at=highlight_data['source_created_at'],
                summary=highlight_data['summary']
            )
            
            # Determine match type
            if data['text_rank'] and data['vector_rank']:
                match_type = "hybrid"
            elif data['text_rank']:
                match_type = "text"
            else:
                match_type = "vector"
            
            search_results.append(SearchResult(
                highlight=highlight,
                source=source,
                score=data['final_score'],
                match_type=match_type
            ))
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error combining results: {e}")
        return []


def search_by_tags(db: Session, tags: List[str], limit: int = 20) -> List[SearchResult]:
    """Search highlights by tags"""
    try:
        # Simple tag-based search
        # In a real implementation, you'd have a proper tag system
        query = db.query(Highlight).join(Source)
        
        for tag in tags:
            query = query.filter(
                Highlight.text.contains(tag) | 
                Source.title.contains(tag)
            )
        
        highlights = query.limit(limit).all()
        
        return [
            SearchResult(
                highlight=highlight,
                source=highlight.source,
                score=1.0,
                match_type="tag"
            )
            for highlight in highlights
        ]
        
    except Exception as e:
        logger.error(f"Error in tag search: {e}")
        return []


def search_articles(db: Session, query: SearchQuery) -> List[Dict[str, Any]]:
    """Search articles using similar hybrid approach"""
    try:
        # Search in articles table
        text_query = text("""
            SELECT 
                a.id,
                a.title,
                a.url,
                a.content,
                a.summary,
                a.author,
                a.published_at,
                a.created_at,
                a.tags,
                (
                    similarity(a.title, :query) * 0.7 +
                    COALESCE(similarity(a.content, :query), 0) * 0.3
                ) as text_score
            FROM articles a
            WHERE 
                a.title ILIKE :like_query OR 
                COALESCE(a.content, '') ILIKE :like_query
            ORDER BY text_score DESC
            LIMIT :limit
        """)
        
        results = db.execute(text_query, {
            "query": query.q,
            "like_query": f"%{query.q}%",
            "limit": query.limit
        }).fetchall()
        
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Error in article search: {e}")
        return [] 