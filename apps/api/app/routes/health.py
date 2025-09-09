from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import redis
import requests
from ..db import get_db
from ..schemas import HealthResponse
from ..config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"
    
    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"
    
    # Check Ollama
    try:
        response = requests.get(f"{settings.ollama_base}/api/tags", timeout=5)
        ollama_status = "ok" if response.status_code == 200 else "error"
    except Exception:
        ollama_status = "error"
    
    return HealthResponse(
        status="healthy" if all(s == "ok" for s in [db_status, redis_status, ollama_status]) else "degraded",
        db=db_status,
        redis=redis_status,
        ollama=ollama_status,
        embeddings_model=settings.emb_model
    ) 