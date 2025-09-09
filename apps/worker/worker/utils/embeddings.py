"""
Embeddings utility module for generating and managing vector embeddings
"""

import logging
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import os

logger = logging.getLogger(__name__)

# Global model instance
_model = None
_model_name = os.getenv('EMB_MODEL', 'BAAI/bge-small-en-v1.5')


def get_model() -> Optional[SentenceTransformer]:
    """Get or initialize the embedding model"""
    global _model
    
    if _model is None:
        try:
            logger.info(f"Loading embedding model: {_model_name}")
            _model = SentenceTransformer(_model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            return None
    
    return _model


def create_embedding(text: str, max_length: int = 512) -> List[float]:
    """Create embedding for text"""
    model = get_model()
    if not model:
        logger.warning("Embedding model not available, returning zeros")
        return [0.0] * 384  # Default dimension
    
    try:
        # Truncate text if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Generate embedding
        embedding = model.encode(text)
        
        # Convert to list and ensure it's the right dimension
        embedding_list = embedding.tolist()
        
        # Ensure 384 dimensions (pad or truncate if necessary)
        if len(embedding_list) < 384:
            embedding_list.extend([0.0] * (384 - len(embedding_list)))
        elif len(embedding_list) > 384:
            embedding_list = embedding_list[:384]
        
        return embedding_list
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return [0.0] * 384


def create_batch_embeddings(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Create embeddings for multiple texts in batches"""
    model = get_model()
    if not model:
        logger.warning("Embedding model not available, returning zeros")
        return [[0.0] * 384 for _ in texts]
    
    try:
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = model.encode(batch)
            
            # Convert to list format
            for emb in batch_embeddings:
                emb_list = emb.tolist()
                # Ensure 384 dimensions
                if len(emb_list) < 384:
                    emb_list.extend([0.0] * (384 - len(emb_list)))
                elif len(emb_list) > 384:
                    emb_list = emb_list[:384]
                embeddings.append(emb_list)
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        return [[0.0] * 384 for _ in texts]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Normalize vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


def find_similar_embeddings(query_embedding: List[float], 
                           embeddings: List[List[float]], 
                           top_k: int = 5) -> List[tuple]:
    """Find top-k most similar embeddings"""
    try:
        similarities = []
        
        for i, emb in enumerate(embeddings):
            similarity = cosine_similarity(query_embedding, emb)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results
        return similarities[:top_k]
        
    except Exception as e:
        logger.error(f"Error finding similar embeddings: {e}")
        return []


def get_embedding_dimension() -> int:
    """Get the dimension of embeddings"""
    return 384  # Default for bge-small-en-v1.5


def is_model_loaded() -> bool:
    """Check if the embedding model is loaded"""
    return _model is not None 