"""Monitoring and metrics for ZgrWise API."""

import time
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.logging import get_logger

logger = get_logger(__name__)

# Create a custom registry
registry = CollectorRegistry()

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections',
    registry=registry
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections',
    registry=registry
)

REDIS_CONNECTIONS = Gauge(
    'redis_connections_active',
    'Number of active Redis connections',
    registry=registry
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type'],
    registry=registry
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type'],
    registry=registry
)

AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['model', 'status'],
    registry=registry
)

AI_REQUEST_DURATION = Histogram(
    'ai_request_duration_seconds',
    'AI request duration in seconds',
    ['model'],
    registry=registry
)

EMBEDDING_REQUESTS = Counter(
    'embedding_requests_total',
    'Total embedding generation requests',
    ['model', 'status'],
    registry=registry
)

SEARCH_REQUESTS = Counter(
    'search_requests_total',
    'Total search requests',
    ['search_type', 'status'],
    registry=registry
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP metrics."""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Extract endpoint (remove query params and path params)
        endpoint = request.url.path
        if endpoint.startswith('/api/'):
            # Normalize API endpoints
            parts = endpoint.split('/')
            if len(parts) > 3:
                endpoint = f"/api/{parts[2]}/{{id}}" if '{' in parts[3] else f"/api/{parts[2]}"
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        return response


def get_health_status() -> Dict[str, Any]:
    """Get detailed health status for monitoring."""
    settings = get_settings()
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.environment,
        "services": {}
    }
    
    # Check database
    try:
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        health_status["services"]["database"] = {
            "status": "healthy",
            "response_time": 0.001  # Placeholder
        }
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        start_time = time.time()
        redis_client.ping()
        response_time = time.time() - start_time
        health_status["services"]["redis"] = {
            "status": "healthy",
            "response_time": response_time
        }
        redis_client.close()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check AI service (if configured)
    if settings.gemini_api_key and settings.gemini_api_key != "your-gemini-api-key-here":
        health_status["services"]["ai"] = {
            "status": "configured",
            "model": settings.ai_model
        }
    else:
        health_status["services"]["ai"] = {
            "status": "not_configured"
        }
    
    return health_status


def get_metrics() -> str:
    """Get Prometheus metrics."""
    return generate_latest(registry)


def update_connection_metrics():
    """Update connection metrics."""
    try:
        settings = get_settings()
        
        # Update Redis connections
        redis_client = redis.from_url(settings.redis_url)
        info = redis_client.info()
        REDIS_CONNECTIONS.set(info.get('connected_clients', 0))
        redis_client.close()
        
        # Update database connections (simplified)
        # In a real implementation, you'd get this from the connection pool
        DATABASE_CONNECTIONS.set(5)  # Placeholder
        
    except Exception as e:
        logger.error(f"Failed to update connection metrics: {e}")


def record_cache_hit(cache_type: str):
    """Record a cache hit."""
    CACHE_HITS.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """Record a cache miss."""
    CACHE_MISSES.labels(cache_type=cache_type).inc()


def record_ai_request(model: str, status: str, duration: float = None):
    """Record an AI API request."""
    AI_REQUESTS.labels(model=model, status=status).inc()
    if duration is not None:
        AI_REQUEST_DURATION.labels(model=model).observe(duration)


def record_embedding_request(model: str, status: str):
    """Record an embedding generation request."""
    EMBEDDING_REQUESTS.labels(model=model, status=status).inc()


def record_search_request(search_type: str, status: str):
    """Record a search request."""
    SEARCH_REQUESTS.labels(search_type=search_type, status=status).inc()
