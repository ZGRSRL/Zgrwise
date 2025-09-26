"""
Scheduler for RSS and AI processing tasks
Handles periodic task scheduling
"""
import os
import time
from datetime import datetime, timedelta
from rq import Queue
from rq_scheduler import Scheduler
from redis import Redis
from worker.tasks.rss_pull import pull_all_feeds
from worker.tasks.normalize import normalize_all_articles
from worker.tasks.ai_tasks import run_ai_for_all_articles
from worker.tasks.embed_articles import embed_all_articles
from worker.tasks.export import export_daily_digest

# Redis connection
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(redis_url)

# Create scheduler
scheduler = Scheduler(connection=redis_conn)

def schedule_rss_tasks():
    """Schedule RSS-related tasks"""
    print("Scheduling RSS tasks...")
    
    # Schedule RSS pull every 15 minutes
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(minutes=1),
        func=pull_all_feeds,
        interval=timedelta(minutes=15),
        id='rss_pull',
        replace=True
    )
    
    # Schedule content normalization every 30 minutes
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(minutes=5),
        func=normalize_all_articles,
        interval=timedelta(minutes=30),
        id='normalize_content',
        replace=True
    )
    
    # Schedule AI processing every hour
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(minutes=10),
        func=run_ai_for_all_articles,
        interval=timedelta(hours=1),
        id='ai_processing',
        replace=True
    )
    
    # Schedule embedding generation every 2 hours
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(minutes=15),
        func=embed_all_articles,
        interval=timedelta(hours=2),
        id='embed_articles',
        replace=True
    )
    
    print("RSS tasks scheduled successfully")

def schedule_daily_tasks():
    """Schedule daily tasks"""
    print("Scheduling daily tasks...")
    
    # Schedule daily digest export at 08:00
    scheduler.schedule(
        scheduled_time=datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0),
        func=export_daily_digest,
        interval=timedelta(days=1),
        id='daily_digest',
        replace=True
    )
    
    print("Daily tasks scheduled successfully")

def run_scheduler():
    """Run the scheduler"""
    print("Starting ZgrWise Scheduler...")
    
    # Schedule all tasks
    schedule_rss_tasks()
    schedule_daily_tasks()
    
    print("All tasks scheduled. Starting scheduler loop...")
    
    try:
        while True:
            # Run scheduled jobs
            scheduler.run()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("Scheduler stopped by user")
    except Exception as e:
        print(f"Scheduler error: {e}")
    finally:
        print("Scheduler shutting down...")

if __name__ == "__main__":
    run_scheduler()