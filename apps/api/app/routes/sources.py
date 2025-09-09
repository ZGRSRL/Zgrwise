from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models import Source
from ..schemas import SourceCreate, SourceResponse

router = APIRouter()


@router.post("/sources", response_model=SourceResponse)
async def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Create a new source"""
    # Check if source already exists by URL
    existing = db.query(Source).filter(Source.url == str(source.url)).first()
    if existing:
        return existing
    
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    return db_source


@router.get("/sources", response_model=List[SourceResponse])
async def get_sources(
    type: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get sources, optionally filtered by type"""
    query = db.query(Source)
    
    if type:
        query = query.filter(Source.type == type)
    
    sources = query.order_by(Source.created_at.desc()).limit(limit).all()
    return sources


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get a specific source by ID"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source


@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int, 
    source_update: SourceCreate, 
    db: Session = Depends(get_db)
):
    """Update a source"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    for field, value in source_update.dict().items():
        setattr(source, field, value)
    
    db.commit()
    db.refresh(source)
    
    return source


@router.delete("/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a source"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(source)
    db.commit()
    
    return {"message": "Source deleted successfully"}