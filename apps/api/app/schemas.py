from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from packages.shared.schemas import SourceType


class SourceCreate(BaseModel):
    type: SourceType
    url: HttpUrl
    origin: str
    title: str
    author: Optional[str] = None
    raw: str
    summary: Optional[str] = None


class SourceResponse(BaseModel):
    id: int
    type: SourceType
    url: str
    origin: str
    title: str
    author: Optional[str] = None
    created_at: datetime
    summary: Optional[str] = None
    
    class Config:
        from_attributes = True


class HighlightCreate(BaseModel):
    source_id: int
    text: str
    note: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = None


class HighlightResponse(BaseModel):
    id: int
    source_id: int
    text: str
    note: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    highlight_id: int
    quality: int  # 0-5


class ReviewResponse(BaseModel):
    id: int
    highlight_id: int
    next_review_at: datetime
    interval: int
    ease: float
    reps: int
    last_result: Optional[int] = None
    
    class Config:
        from_attributes = True


class RSSFeedCreate(BaseModel):
    url: HttpUrl
    title: str
    category: Optional[str] = "general"


class RSSFeedResponse(BaseModel):
    id: int
    url: str
    title: str
    category: str
    added_at: datetime
    last_checked: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    id: int
    feed_id: int
    title: str
    url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class AIReviewRequest(BaseModel):
    highlight_id: int


class QuizQuestion(BaseModel):
    question: str
    correct_answer: str
    options: List[str]
    explanation: str


class SearchQuery(BaseModel):
    q: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20


class SearchResult(BaseModel):
    highlight: HighlightResponse
    source: SourceResponse
    score: float
    match_type: str


class HealthResponse(BaseModel):
    status: str
    db: str
    redis: str
    ollama: str
    embeddings_model: str


class IngestWebRequest(BaseModel):
    url: HttpUrl
    html: Optional[str] = None


class IngestPDFRequest(BaseModel):
    file: bytes


class IngestYouTubeRequest(BaseModel):
    video_url: HttpUrl


class AIRequest(BaseModel):
    text: str


class AIResponse(BaseModel):
    result: str
    model: str


class AIReviewRequest(BaseModel):
    highlight_id: int


class AIReviewResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str 