"""
Review and spaced repetition tasks
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from worker.utils.db import get_db_session
from worker.utils.models import Review, Highlight

logger = logging.getLogger(__name__)


def schedule_daily_reviews() -> Dict[str, Any]:
    """Schedule daily review sessions"""
    try:
        with get_db_session() as db:
            # Get highlights due for review
            now = datetime.now()
            due_reviews = db.query(Review).filter(Review.next_review_at <= now).all()
            
            logger.info(f"Scheduled {len(due_reviews)} reviews for today")
            return {"status": "success", "review_count": len(due_reviews)}
            
    except Exception as e:
        logger.error(f"Error scheduling daily reviews: {e}")
        return {"status": "error", "message": str(e)}


def process_review_result(review_id: int, quality: int) -> Dict[str, Any]:
    """Process a review result and update spaced repetition parameters"""
    try:
        with get_db_session() as db:
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                return {"status": "error", "message": "Review not found"}
            
            # Update review parameters based on quality
            if quality >= 3:
                # Good response
                review.ease = min(2.5, review.ease + 0.1)
                if review.reps == 0:
                    review.interval = 1
                elif review.reps == 1:
                    review.interval = 3
                else:
                    review.interval = int(review.ease * review.interval)
                review.reps += 1
            else:
                # Poor response
                review.ease = max(1.3, review.ease - 0.2)
                review.interval = 1
                review.reps = 0
            
            # Calculate next review date
            review.next_review_at = datetime.now() + timedelta(days=review.interval)
            review.last_result = quality
            
            db.commit()
            
            logger.info(f"Updated review {review_id} with quality {quality}")
            return {"status": "success", "next_review": review.next_review_at}
            
    except Exception as e:
        logger.error(f"Error processing review result: {e}")
        return {"status": "error", "message": str(e)}


def get_review_queue(limit: int = 20) -> Dict[str, Any]:
    """Get highlights that are due for review"""
    try:
        with get_db_session() as db:
            now = datetime.now()
            due_reviews = db.query(Review).filter(Review.next_review_at <= now).limit(limit).all()
            
            # Get highlight details
            review_data = []
            for review in due_reviews:
                highlight = db.query(Highlight).filter(Highlight.id == review.highlight_id).first()
                if highlight:
                    review_data.append({
                        "review_id": review.id,
                        "highlight_id": highlight.id,
                        "text": highlight.text,
                        "note": highlight.note,
                        "next_review_at": review.next_review_at,
                        "interval": review.interval,
                        "ease": review.ease,
                        "reps": review.reps
                    })
            
            return {"status": "success", "reviews": review_data}
            
    except Exception as e:
        logger.error(f"Error getting review queue: {e}")
        return {"status": "error", "message": str(e)}


def create_initial_review(highlight_id: int) -> Dict[str, Any]:
    """Create initial review for a new highlight"""
    try:
        with get_db_session() as db:
            # Check if review already exists
            existing = db.query(Review).filter(Review.highlight_id == highlight_id).first()
            if existing:
                return {"status": "error", "message": "Review already exists"}
            
            # Create new review
            review = Review(
                highlight_id=highlight_id,
                next_review_at=datetime.now() + timedelta(days=1),
                interval=1,
                ease=2.5,
                reps=0
            )
            
            db.add(review)
            db.commit()
            
            logger.info(f"Created initial review for highlight {highlight_id}")
            return {"status": "success", "review_id": review.id}
            
    except Exception as e:
        logger.error(f"Error creating initial review: {e}")
        return {"status": "error", "message": str(e)} 