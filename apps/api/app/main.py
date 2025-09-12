from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from .routes import health, highlights, search, review, ai, rss, ai_review, sources, rss_native, export
from .config import settings
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ZgrWise API",
    description="Knowledge Management System API",
    version="1.0.0"
)

# CORS middleware
ALLOWED_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(rss.router, prefix="/api", tags=["rss"], dependencies=[Depends(verify_api_key)])
app.include_router(rss_native.router, tags=["rss-native"])  # No API key required for native RSS
app.include_router(ai_review.router, prefix="/api", tags=["ai-review"], dependencies=[Depends(verify_api_key)])
app.include_router(sources.router, prefix="/api", tags=["sources"], dependencies=[Depends(verify_api_key)])
app.include_router(export.router, tags=["export"], dependencies=[Depends(verify_api_key)])

@app.get("/")
async def root():
    return {"message": "ZgrWise API is running"} 