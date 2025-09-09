"""
Cron job scheduler for periodic tasks
"""

import logging
import schedule
import time
from datetime import datetime, timedelta
from worker.tasks.rss_enhanced import fetch_all_rss_feeds, get_feed_statistics
from worker.tasks.review import schedule_daily_reviews
from worker.utils.db import get_db_session
from worker.utils.models import RSSFeed, Review

logger = logging.getLogger(__name__)


def setup_scheduler():
    """Setup all scheduled jobs"""
    
    # RSS Feed Processing
    schedule.every(30).minutes.do(fetch_all_rss_feeds)
    schedule.every().hour.do(cleanup_old_articles)
    
    # Review Scheduling
    schedule.every().day.at("09:00").do(schedule_daily_reviews)
    schedule.every().day.at("18:00").do(send_review_reminders)
    
    # Maintenance Tasks
    schedule.every().day.at("02:00").do(cleanup_old_data)
    schedule.every().sunday.at("03:00").do(weekly_analytics)
    
    logger.info("Scheduler setup completed")


def run_scheduler():
    """Run the scheduler loop"""
    logger.info("Starting scheduler...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            time.sleep(60)


def cleanup_old_articles():
    """Clean up old articles (keep last 1000)"""
    try:
        with get_db_session() as db:
            # Get total count
            total_articles = db.query(Article).count()
            
            if total_articles > 1000:
                # Delete old articles, keeping the most recent 1000
                articles_to_delete = db.query(Article).order_by(Article.created_at.desc()).offset(1000).all()
                
                for article in articles_to_delete:
                    db.delete(article)
                
                db.commit()
                logger.info(f"Cleaned up {len(articles_to_delete)} old articles")
                
    except Exception as e:
        logger.error(f"Error cleaning up old articles: {e}")


def send_review_reminders():
    """Send reminders for highlights due for review"""
    try:
        with get_db_session() as db:
            # Get highlights due for review in the next 24 hours
            tomorrow = datetime.now() + timedelta(days=1)
            due_reviews = db.query(Review).filter(Review.next_review_at <= tomorrow).all()
            
            if due_reviews:
                logger.info(f"Sending reminders for {len(due_reviews)} highlights due for review")
                
                # In a real implementation, you'd send notifications here
                # For now, just log the information
                for review in due_reviews:
                    logger.info(f"Reminder: Review highlight {review.highlight_id} due at {review.next_review_at}")
                    
    except Exception as e:
        logger.error(f"Error sending review reminders: {e}")


def cleanup_old_data():
    """Clean up old data and optimize database"""
    try:
        with get_db_session() as db:
            # Clean up old review sessions (older than 90 days)
            cutoff_date = datetime.now() - timedelta(days=90)
            old_sessions = db.query(ReviewSession).filter(ReviewSession.created_at < cutoff_date).all()
            
            for session in old_sessions:
                db.delete(session)
            
            db.commit()
            logger.info(f"Cleaned up {len(old_sessions)} old review sessions")
            
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")


def weekly_analytics():
    """Generate weekly analytics report"""
    try:
        with get_db_session() as db:
            # Get RSS feed statistics
            rss_stats = get_feed_statistics()
            
            # Get learning progress
            total_highlights = db.query(Highlight).count()
            total_reviews = db.query(Review).count()
            total_sessions = db.query(ReviewSession).count()
            
            # Calculate weekly progress
            week_ago = datetime.now() - timedelta(days=7)
            weekly_highlights = db.query(Highlight).filter(Highlight.created_at >= week_ago).count()
            weekly_reviews = db.query(ReviewSession).filter(ReviewSession.created_at >= week_ago).count()
            
            analytics = {
                "rss_stats": rss_stats,
                "total_highlights": total_highlights,
                "total_reviews": total_reviews,
                "total_sessions": total_sessions,
                "weekly_highlights": weekly_highlights,
                "weekly_reviews": weekly_reviews,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Weekly analytics generated: {analytics}")
            
            # In a real implementation, you'd save this to a file or send via email
            
    except Exception as e:
        logger.error(f"Error generating weekly analytics: {e}")


def manual_rss_refresh():
    """Manually refresh all RSS feeds"""
    try:
        logger.info("Manual RSS refresh started")
        fetch_all_rss_feeds()
        logger.info("Manual RSS refresh completed")
    except Exception as e:
        logger.error(f"Error in manual RSS refresh: {e}")


def manual_review_scheduling():
    """Manually schedule daily reviews"""
    try:
        logger.info("Manual review scheduling started")
        schedule_daily_reviews()
        logger.info("Manual review scheduling completed")
    except Exception as e:
        logger.error(f"Error in manual review scheduling: {e}")


if __name__ == "__main__":
    # Setup and run scheduler
    setup_scheduler()
    run_scheduler() 