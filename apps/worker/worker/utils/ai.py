"""
AI utilities for the worker
"""

import requests
import os
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE = os.getenv('OLLAMA_BASE', 'http://localhost:11434')


def summarize_text(text: str) -> str:
    """Summarize text using Ollama"""
    try:
        prompt = f"TL;DR (max 2 cümle): {text}"
        
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            # Fallback
            words = text.split()[:20]
            return " ".join(words) + "..."
            
    except Exception as e:
        logger.warning(f"Could not generate summary: {e}")
        # Fallback
        words = text.split()[:20]
        return " ".join(words) + "..."


def generate_tags(text: str) -> str:
    """Generate tags for text using Ollama"""
    try:
        prompt = f"İçeriğe 3–7 arası kısa, virgülle ayrılmış etiket öner: {text}"
        
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            # Fallback tags
            return "bilgi, öğrenme, not"
            
    except Exception as e:
        logger.warning(f"Could not generate tags: {e}")
        # Fallback tags
        return "bilgi, öğrenme, not" 