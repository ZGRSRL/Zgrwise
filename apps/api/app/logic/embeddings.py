# Yer tutucu: embedding yoksa arama yine çalışsın diye boş bırakıyoruz.
# İleride sentence-transformers ile gerçek vektör eklenir.
from typing import List, Optional
import numpy as np

def embed_texts(texts: List[str]) -> list[list[float]]:
    return [[0.0] * 8 for _ in texts]  # dummy

def create_embedding(text: str, model: str = "dummy") -> Optional[List[float]]:
    """Create embedding for a single text."""
    if not text or not text.strip():
        return None
    # Return dummy embedding for now
    return [0.0] * 384  # Standard embedding dimension