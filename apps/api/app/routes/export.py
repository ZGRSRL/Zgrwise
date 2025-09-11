from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models_rss import RSSItem
import os, pathlib

router = APIRouter(prefix="/api/export", tags=["export"])

EXPORT_DIR = pathlib.Path(os.getenv("OBSIDIAN_EXPORT_PATH","/data/exports"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/md")
def export_md(db: Session = Depends(get_db)):
    items = db.query(RSSItem).filter(RSSItem.status.in_(["processed","indexed"]))\
             .order_by(RSSItem.id.desc()).limit(100).all()
    count = 0
    for it in items:
        name = f"{it.id}-{(it.title or 'note').strip().replace(' ','_')[:60]}.md"
        p = EXPORT_DIR / name
        with open(p, 'w', encoding='utf-8') as f:
            f.write(f"---\ntitle: {it.title or ''}\nlink: {it.link}\n---\n\n")
            f.write(it.content_text or '')
        count += 1
    return {"written": count, "dir": str(EXPORT_DIR)}