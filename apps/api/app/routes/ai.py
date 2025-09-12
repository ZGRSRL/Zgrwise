from fastapi import APIRouter, HTTPException
import requests
from ..schemas import AIRequest, AIResponse
from ..config import settings

router = APIRouter()


@router.post("/ai/summarize", response_model=AIResponse)
async def summarize_text(request: AIRequest):
    """Summarize text using Gemini API"""
    try:
        prompt = f"TL;DR (max 2 cümle): {request.text}"
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent",
            params={"key": settings.GEMINI_API_KEY},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            return AIResponse(result=summary, model=settings.AI_MODEL)
        else:
            # Fallback to simple summary
            words = request.text.split()[:20]
            summary = " ".join(words) + "..."
            return AIResponse(result=summary, model="fallback")
            
    except Exception as e:
        # Graceful degradation
        words = request.text.split()[:20]
        summary = " ".join(words) + "..."
        return AIResponse(result=summary, model="fallback")


@router.post("/ai/autotag", response_model=AIResponse)
async def autotag_text(request: AIRequest):
    """Generate tags for text using Gemini API"""
    try:
        prompt = f"İçeriğe 3–7 arası kısa, virgülle ayrılmış etiket öner: {request.text}"
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent",
            params={"key": settings.GEMINI_API_KEY},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            tags = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            return AIResponse(result=tags, model=settings.AI_MODEL)
        else:
            # Fallback tags
            fallback_tags = "bilgi, öğrenme, not"
            return AIResponse(result=fallback_tags, model="fallback")
            
    except Exception as e:
        # Graceful degradation
        fallback_tags = "bilgi, öğrenme, not"
        return AIResponse(result=fallback_tags, model="fallback") 