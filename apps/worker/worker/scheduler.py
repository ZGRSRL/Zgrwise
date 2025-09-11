import os, time, redis, rq
from apps.api.app.db import SessionLocal
from apps.api.app.models_rss import RSSFeed

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

def loop():
    q = rq.Queue("rss", connection=redis.from_url(redis_url))
    while True:
        db = SessionLocal()
        try:
            for f in db.query(RSSFeed).filter_by(active=True).all():
                q.enqueue("worker.tasks.rss_tasks.fetch_and_process_feed", f.id)
                print(f"Queued feed: {f.title} ({f.url})")
        except Exception as e:
            print(f"Scheduler error: {e}")
        finally:
            db.close()
        time.sleep(900)  # 15 dk

if __name__ == "__main__":
    print("RSS Scheduler started - checking feeds every 15 minutes")
    loop()