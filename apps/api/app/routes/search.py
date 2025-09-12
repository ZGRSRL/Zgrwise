from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search(q: str, db: Session = Depends(get_db)):
    if not q or not q.strip():
        return {"items": []}
    
    sql = text("""
        SELECT id, title, link, published_at,
               similarity(coalesce(title,'') || ' ' || coalesce(content_text,''), :q) AS score
        FROM rss_items
        WHERE (title ILIKE '%'||:q||'%' OR content_text ILIKE '%'||:q||'%')
        ORDER BY score DESC NULLS LAST
        LIMIT 50
    """)
    rows = db.execute(sql, {"q": q.strip()}).mappings().all()
    return {"items": [dict(r) for r in rows]} 