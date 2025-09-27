#!/usr/bin/env python3
"""
Basit test API'si - ZgrWise özelliklerini göstermek için
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import time

app = FastAPI(
    title="ZgrWise Test API",
    description="Basit test API'si",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basit modeller
class HealthResponse(BaseModel):
    status: str
    timestamp: float

class RSSFeed(BaseModel):
    id: int
    title: str
    url: str
    category: str
    added_at: str

class RSSItem(BaseModel):
    id: int
    feed_id: int
    title: str
    url: str
    content: Optional[str] = None
    published_at: Optional[str] = None

# Örnek veriler
sample_feeds = [
    RSSFeed(id=1, title="TechCrunch", url="https://techcrunch.com/feed/", category="tech", added_at="2024-01-01T00:00:00Z"),
    RSSFeed(id=2, title="Hacker News", url="https://hnrss.org/frontpage", category="tech", added_at="2024-01-01T00:00:00Z"),
    RSSFeed(id=3, title="Ars Technica", url="https://feeds.arstechnica.com/arstechnica/index/", category="tech", added_at="2024-01-01T00:00:00Z"),
]

sample_items = [
    RSSItem(id=1, feed_id=1, title="AI Breakthrough", url="https://example.com/ai", content="Amazing AI development", published_at="2024-01-01T12:00:00Z"),
    RSSItem(id=2, feed_id=1, title="New Framework", url="https://example.com/framework", content="Revolutionary web framework", published_at="2024-01-01T13:00:00Z"),
    RSSItem(id=3, feed_id=2, title="Startup News", url="https://example.com/startup", content="Exciting startup funding", published_at="2024-01-01T14:00:00Z"),
]

@app.get("/")
async def root():
    return {
        "message": "ZgrWise Test API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "feeds": "/api/rss/feeds",
            "items": "/api/rss/items",
            "search": "/api/search?q=query"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )

@app.get("/api/rss/feeds", response_model=List[RSSFeed])
async def get_feeds():
    """RSS feed'lerini listele"""
    return sample_feeds

@app.get("/api/rss/items", response_model=List[RSSItem])
async def get_items(feed_id: Optional[int] = None, limit: int = 20):
    """RSS item'larını listele"""
    items = sample_items
    if feed_id:
        items = [item for item in items if item.feed_id == feed_id]
    return items[:limit]

@app.get("/api/search")
async def search(q: str, limit: int = 20):
    """Basit arama"""
    if not q:
        return {"results": [], "query": q, "total": 0}
    
    # Basit text arama
    results = []
    for item in sample_items:
        if q.lower() in item.title.lower() or (item.content and q.lower() in item.content.lower()):
            results.append({
                "id": item.id,
                "title": item.title,
                "url": item.url,
                "content": item.content,
                "feed_id": item.feed_id,
                "published_at": item.published_at
            })
    
    return {
        "results": results[:limit],
        "query": q,
        "total": len(results)
    }

@app.post("/api/rss/feeds")
async def add_feed(feed: RSSFeed):
    """Yeni RSS feed ekle"""
    new_id = max([f.id for f in sample_feeds]) + 1
    feed.id = new_id
    sample_feeds.append(feed)
    return {"message": "Feed added successfully", "feed": feed}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
