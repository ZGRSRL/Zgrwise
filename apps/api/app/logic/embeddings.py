# Yer tutucu: embedding yoksa arama yine çalışsın diye boş bırakıyoruz.
# İleride sentence-transformers ile gerçek vektör eklenir.
from typing import List

def embed_texts(texts: List[str]) -> list[list[float]]:
    return [[0.0] * 8 for _ in texts]  # dummy