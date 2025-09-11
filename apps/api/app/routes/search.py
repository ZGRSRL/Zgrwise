from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db

router = APIRouter(prefix="/api", tags=["search"])

@router.post("/search")
def search(payload: dict, db: Session = Depends(get_db)):
    q = (payload.get("q") or "").strip()
    lim = int(payload.get("limit") or 20)
    if not q:
        return {"items": []}
    # Basit full-text benzeri: title/content_text üzerinde trigram + ILIKE kombinasyonu
    sql = text(
        """
        select id, title, link, published_at,
               similarity(coalesce(title,'') || ' ' || coalesce(content_text,''), :q) as score
        from rss_items
        where (title ilike :pat or content_text ilike :pat)
        order by score desc nulls last, published_at desc nulls last
        limit :lim
        """
    )
    rows = db.execute(sql, {"q": q, "pat": f"%{q}%", "lim": lim}).mappings().all()
    return {"items": [dict(r) for r in rows]} 