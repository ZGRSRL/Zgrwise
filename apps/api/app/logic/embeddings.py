"""
Embedding utilities
"""
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize model
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def create_embedding(text: str) -> list:
    """
    Create embedding for text
    
    Args:
        text: Text to embed
        
    Returns:
        List of embedding values
    """
    if not text:
        return [0.0] * 384
    
    try:
        embedding = _model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return [0.0] * 384


def get_embedding_model():
    """Get the embedding model instance"""
    return _model