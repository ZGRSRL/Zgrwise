from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..schemas import SearchQuery, SearchResult
from ..logic.search import hybrid_search

router = APIRouter()


@router.post("/search", response_model=List[SearchResult])
async def search_highlights(query: SearchQuery, db: Session = Depends(get_db)):
    """Search highlights using hybrid search (text + vector)"""
    return hybrid_search(db, query) 