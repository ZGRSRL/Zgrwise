from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class SourceType(str, Enum):
    WEB = "web"
    PDF = "pdf"
    YOUTUBE = "youtube"
    NEWSLETTER = "newsletter"
    KINDLE = "kindle"
    RSS = "rss"


class Source(BaseModel):
    id: Optional[int] = None
    type: SourceType
    url: HttpUrl
    origin: str
    title: str
    author: Optional[str] = None
    created_at: datetime
    raw: str
    summary: Optional[str] = None
    tags: List[str] = []


class Highlight(BaseModel):
    id: Optional[int] = None
    source_id: int
    text: str
    note: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    tags: List[str] = []


class Embedding(BaseModel):
    id: Optional[int] = None
    object_type: str  # 'source' or 'highlight'
    object_id: int
    model: str
    vector: List[float]  # 384 dimensions


class Review(BaseModel):
    id: Optional[int] = None
    highlight_id: int
    next_review_at: datetime
    interval: int  # days
    ease: float
    reps: int
    last_result: Optional[int] = None  # 0-5


class RSSFeed(BaseModel):
    id: Optional[int] = None
    url: HttpUrl
    title: str
    added_at: datetime
    last_checked: Optional[datetime] = None


class Export(BaseModel):
    id: Optional[int] = None
    target: str  # 'obsidian'
    status: str
    last_run_at: Optional[datetime] = None
    config_json: dict


class SearchQuery(BaseModel):
    q: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20


class SearchResult(BaseModel):
    highlight: Highlight
    source: Source
    score: float
    match_type: str  # 'text', 'vector', or 'hybrid'


class IngestWebRequest(BaseModel):
    url: HttpUrl
    html: Optional[str] = None


class IngestPDFRequest(BaseModel):
    file: bytes


class IngestYouTubeRequest(BaseModel):
    video_url: HttpUrl


class ReviewAnswer(BaseModel):
    highlight_id: int
    quality: int  # 0-5


class AIRequest(BaseModel):
    text: str


class AIResponse(BaseModel):
    result: str
    model: str 