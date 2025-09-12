import requests, feedparser, hashlib, dateutil.parser
from sqlalchemy.orm import Session
from worker.utils.db import get_db_session   # küçük yardımcı: SessionLocal()
from apps.api.app.models import RSSFeed, RSSItem
from trafilatura import extract as tr_extract
from urllib.parse import urlsplit
import os, json

OLLAMA = os.getenv("OLLAMA_BASE","http://ollama:11434")

def _normalize_guid(gid: str, link: str) -> str:
    base = (gid or "").strip() or (link or "").strip()
    # link'te query/frag ayıklayalım, küçük harfleyelim
    if base.startswith("http"):
        u = urlsplit(base)
        base = f"{u.scheme}://{u.netloc}{u.path}".lower()
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def _guid_key(e):
    gid = getattr(e, "id", None) or (e.get("id") if isinstance(e, dict) else "")
    link = getattr(e, "link", None) or (e.get("link") if isinstance(e, dict) else "")
    return _normalize_guid(gid, link)

def fetch_and_process_feed(feed_id: int):
    db: Session = get_db_session()
    feed = db.get(RSSFeed, feed_id)
    if not feed or not feed.active: 
        db.close()
        return

    headers = {}
    if feed.etag: headers["If-None-Match"] = feed.etag
    if feed.last_modified: headers["If-Modified-Since"] = feed.last_modified

    try:
        r = requests.get(feed.url, headers=headers, timeout=20)
        if r.status_code == 304: 
            db.close()
            return
        data = feedparser.parse(r.content)

        # etag/last_modified güncelle
        feed.etag = r.headers.get("ETag") or feed.etag
        feed.last_modified = r.headers.get("Last-Modified") or feed.last_modified
        db.add(feed)
        db.commit()

        for e in data.entries:
            key = _guid_key(e)
            exists = db.query(RSSItem).filter_by(feed_id=feed.id, guid=key).first()
            if exists: continue

            published = None
            try:
                published = dateutil.parser.parse(getattr(e, "published", "") or getattr(e, "updated", ""))
            except: pass

            item = RSSItem(
                feed_id=feed.id,
                guid=key,
                link=getattr(e,"link",None) or "",
                title=getattr(e,"title",None),
                published_at=published,
                content_text=""
            )
            
            # İçerik çıkar (link'ten)
            try:
                html = requests.get(item.link, timeout=20).text
                text = tr_extract(html, include_tables=False) or ""
                item.content_text = text.strip()
            except: pass

            db.add(item)
            db.commit()

    except Exception as e:
        print(f"Error processing feed {feed_id}: {e}")
    finally:
        db.close()