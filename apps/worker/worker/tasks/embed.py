"""
Embedding generation tasks
"""

import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from worker.utils.db import get_db_session
from worker.utils.models import Source, Highlight

logger = logging.getLogger(__name__)

# Load the embedding model
try:
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    logger.info("Embedding model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    model = None


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text"""
    if not model:
        logger.warning("Embedding model not available, returning zeros")
        return [0.0] * 384
    
    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return [0.0] * 384


def process_source_embeddings(source_id: int) -> Dict[str, Any]:
    """Process embeddings for a source"""
    try:
        with get_db_session() as db:
            # Get source content
            source = db.query(Source).filter(Source.id == source_id).first()
            if not source:
                return {"status": "error", "message": "Source not found"}
            
            # Generate embedding
            embedding = generate_embedding(source.raw[:1000])  # Limit text length
            
            # TODO: Save embedding to database
            logger.info(f"Generated embedding for source {source_id}")
            
            return {"status": "success", "embedding": embedding}
            
    except Exception as e:
        logger.error(f"Error processing source embeddings: {e}")
        return {"status": "error", "message": str(e)}


def process_highlight_embeddings(highlight_id: int) -> Dict[str, Any]:
    """Process embeddings for a highlight"""
    try:
        with get_db_session() as db:
            # Get highlight content
            highlight = db.query(Highlight).filter(Highlight.id == highlight_id).first()
            if not highlight:
                return {"status": "error", "message": "Highlight not found"}
            
            # Generate embedding
            embedding = generate_embedding(highlight.text)
            
            # TODO: Save embedding to database
            logger.info(f"Generated embedding for highlight {highlight_id}")
            
            return {"status": "success", "embedding": embedding}
            
    except Exception as e:
        logger.error(f"Error processing highlight embeddings: {e}")
        return {"status": "error", "message": str(e)} 