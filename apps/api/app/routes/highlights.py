from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models import Highlight, Source
from ..schemas import HighlightCreate, HighlightResponse

router = APIRouter()


@router.post("/highlights", response_model=HighlightResponse)
async def create_highlight(highlight: HighlightCreate, db: Session = Depends(get_db)):
    """Create a new highlight"""
    # Verify source exists
    source = db.query(Source).filter(Source.id == highlight.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db_highlight = Highlight(**highlight.dict())
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    
    return db_highlight


@router.get("/highlights", response_model=List[HighlightResponse])
async def get_highlights(
    source_id: int = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get highlights, optionally filtered by source_id"""
    query = db.query(Highlight)
    
    if source_id:
        query = query.filter(Highlight.source_id == source_id)
    
    highlights = query.limit(limit).all()
    return highlights


@router.get("/highlights/{highlight_id}", response_model=HighlightResponse)
async def get_highlight(highlight_id: int, db: Session = Depends(get_db)):
    """Get a specific highlight by ID"""
    highlight = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    
    return highlight 