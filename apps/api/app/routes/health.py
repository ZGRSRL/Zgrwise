from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
import time
from ..db import get_db
from ..schemas import HealthResponse
from ..config import get_settings
# from ..monitoring import get_health_status, get_metrics, update_connection_metrics
from ..logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Basic health check endpoint"""
    settings = get_settings()
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
    
    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        redis_status = "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "error"
    
    # Determine overall status
    overall_status = "healthy" if all(s == "ok" for s in [db_status, redis_status]) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        db=db_status,
        redis=redis_status,
        timestamp=time.time()
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    return {"status": "healthy", "message": "Detailed health check not available"}


@router.get("/healthz")
async def kubernetes_health_check():
    """Kubernetes-style health check endpoint"""
    settings = get_settings()
    
    try:
        # Quick database check
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        # Quick Redis check
        r = redis.from_url(settings.redis_url)
        r.ping()
        r.close()
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Response(
            content='{"status": "error"}',
            status_code=503,
            media_type="application/json"
        )


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return {"message": "Metrics not available"} 