"""
Article Embedding Generation Tasks
Handles vector embedding generation for articles
"""
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models import Article, ArticleEmbedding
import numpy as np

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize model
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_session():
    """Get database session"""
    return SessionLocal()


def chunk(md: str, limit_words=300):
    """
    Split markdown content into chunks for embedding
    
    Args:
        md: Markdown content
        limit_words: Maximum words per chunk
        
    Returns:
        List of text chunks
    """
    if not md:
        return []
    
    parts, cur, cnt = [], [], 0
    
    for p in (md or "").split("\n\n"):
        w = len(p.split())
        if cnt + w > limit_words and cur:
            parts.append("\n\n".join(cur))
            cur, cnt = [], 0
        cur.append(p)
        cnt += w
    
    if cur:
        parts.append("\n\n".join(cur))
    
    return parts


def embed_article(article_id):
    """
    Generate embeddings for an article
    
    Args:
        article_id: ID of the article to embed
    """
    db = get_session()
    try:
        article = db.query(Article).get(article_id)
        if not article:
            print(f"Article with ID {article_id} not found")
            return
        
        if not article.content_md:
            print(f"Article {article_id} has no markdown content - skipping embedding")
            return
        
        print(f"Generating embeddings for article: {article.title}")
        
        # Check if embeddings already exist
        existing = db.query(ArticleEmbedding).filter_by(article_id=article_id).first()
        if existing:
            print(f"Embeddings already exist for article {article_id}")
            return
        
        # Chunk the content
        chunks = chunk(article.content_md)
        if not chunks:
            print(f"No chunks generated for article {article_id}")
            return
        
        # Generate embeddings
        vectors = _model.encode(chunks, normalize_embeddings=True)
        
        # Save embeddings to database
        for text, vector in zip(chunks, vectors):
            embedding = ArticleEmbedding(
                article_id=article_id,
                model="sentence-transformers/all-MiniLM-L6-v2",
                vector=vector.tolist()
            )
            db.add(embedding)
        
        db.commit()
        print(f"Successfully generated {len(chunks)} embeddings for article: {article.title}")
        
    except Exception as e:
        print(f"Error generating embeddings for article {article_id}: {e}")
        db.rollback()
    finally:
        db.close()


def embed_all_articles():
    """Generate embeddings for all articles that don't have them yet"""
    db = get_session()
    try:
        # Find articles that have markdown content but no embeddings
        articles = db.query(Article).filter(
            Article.content_md.isnot(None)
        ).all()
        
        articles_without_embeddings = []
        for article in articles:
            existing = db.query(ArticleEmbedding).filter_by(article_id=article.id).first()
            if not existing:
                articles_without_embeddings.append(article)
        
        print(f"Found {len(articles_without_embeddings)} articles without embeddings")
        
        for article in articles_without_embeddings:
            embed_article(article.id)
            
    except Exception as e:
        print(f"Error in embed_all_articles: {e}")
    finally:
        db.close()


def embed_article_batch(article_ids):
    """
    Generate embeddings for a batch of articles
    
    Args:
        article_ids: List of article IDs to embed
    """
    for article_id in article_ids:
        embed_article(article_id)