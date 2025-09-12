from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import RSSFeed, RSSItem
from pydantic import BaseModel
from datetime import datetime, timezone
import hashlib
import redis
import rq

router = APIRouter(prefix="/api/rss", tags=["rss"])

class FeedIn(BaseModel):
    url: str
    title: str | None = None

@router.post("/feeds")
def add_feed(feed: FeedIn, db: Session = Depends(get_db)):
    obj = RSSFeed(url=feed.url, title=feed.title)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "url": obj.url, "title": obj.title}

@router.get("/feeds")
def list_feeds(db: Session = Depends(get_db)):
    return db.query(RSSFeed).order_by(RSSFeed.id.desc()).all()

@router.post("/refresh/{feed_id}")
def refresh_feed(feed_id: int, db: Session = Depends(get_db)):
    # Worker'a kuyrukla – RQ kullanıyoruz:
    try:
        r = redis.from_url("redis://redis:6379/0")
        q = rq.Queue("rss", connection=r)
        q.enqueue("worker.tasks.rss_tasks.fetch_and_process_feed", feed_id)
        return {"queued": True, "feed_id": feed_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue job: {str(e)}")

@router.get("/items")
def list_items(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(RSSItem).order_by(RSSItem.published_at.desc().nullslast(), RSSItem.id.desc()).limit(limit).all()

# ——— Dışa "okunabilir RSS" (son özetler) ———
from fastapi.responses import Response

def _rss_esc(s: str) -> str:
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

@router.get("/outbox.xml")
def outbox(db: Session = Depends(get_db)):
    items = (db.query(RSSItem)
               .filter(RSSItem.status.in_(["processed","indexed"]))
               .order_by(RSSItem.published_at.desc().nullslast(), RSSItem.id.desc())
               .limit(50).all())
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    parts = [f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>ZgrWise Highlights</title>
<link>http://localhost:3000</link>
<description>Latest highlights & summaries</description>
<lastBuildDate>{now}</lastBuildDate>"""]
    for it in items:
        parts.append(f"""<item>
<title>{_rss_esc(it.title or "(no title)")}</title>
<link>{_rss_esc(it.link)}</link>
<guid isPermaLink="false">{_rss_esc(it.guid_hash)}</guid>
<pubDate>{(it.published_at or datetime.now(timezone.utc)).strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
<description><![CDATA[{it.summary_html or (it.content_text or "")[:1000]}]]></description>
</item>""")
    parts.append("</channel></rss>")
    return Response("".join(parts), media_type="application/rss+xml")