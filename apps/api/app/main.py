from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from .routes import health, highlights, search, review, ai, ai_review, sources, export
# from .routes import rss_native  # Geçici olarak devre dışı
# from .routes import rss  # Geçici olarak devre dışı
from .config import get_settings
from .logging import setup_logging, RequestLoggingMiddleware
# from .monitoring import MetricsMiddleware
import os

# Set up logging
setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

# Get settings
settings = get_settings()

app = FastAPI(
    title="ZgrWise API",
    description="Knowledge Management System API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add monitoring middleware
# app.add_middleware(MetricsMiddleware)

# Add request logging middleware
if settings.LOG_REQUESTS:
    app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
ALLOWED_ORIGINS = settings.CORS_ALLOW_ORIGINS.split(",") if settings.CORS_ALLOW_ORIGINS else ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(",") if settings.CORS_ALLOW_METHODS else ["*"],
    allow_headers=settings.CORS_ALLOW_HEADERS.split(",") if settings.CORS_ALLOW_HEADERS else ["*"],
)

# API key dependency
async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(highlights.router, prefix="/api", tags=["highlights"], dependencies=[Depends(verify_api_key)])
app.include_router(search.router, prefix="/api", tags=["search"], dependencies=[Depends(verify_api_key)])
app.include_router(review.router, prefix="/api", tags=["review"], dependencies=[Depends(verify_api_key)])
app.include_router(ai.router, prefix="/api", tags=["ai"], dependencies=[Depends(verify_api_key)])
# app.include_router(rss.router, prefix="/api", tags=["rss"], dependencies=[Depends(verify_api_key)])
# app.include_router(rss_native.router, tags=["rss-native"])  # No API key required for native RSS
app.include_router(ai_review.router, prefix="/api", tags=["ai-review"], dependencies=[Depends(verify_api_key)])
app.include_router(sources.router, prefix="/api", tags=["sources"], dependencies=[Depends(verify_api_key)])
app.include_router(export.router, tags=["export"], dependencies=[Depends(verify_api_key)])

@app.get("/")
async def root():
    return {"message": "ZgrWise API is running"} 