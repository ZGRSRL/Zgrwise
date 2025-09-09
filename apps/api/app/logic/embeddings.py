"""
Embeddings utilities for ZgrWise
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def create_embedding(text: str) -> List[float]:
    """Create a simple embedding - return zeros for now"""
    return [0.0] * 384


def create_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings for multiple texts"""
    return [[0.0] * 384 for _ in texts]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    return 0.0