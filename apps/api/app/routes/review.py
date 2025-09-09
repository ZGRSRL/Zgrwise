from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..db import get_db
from ..models import Review, Highlight
from ..schemas import ReviewCreate, ReviewResponse
from ..logic.sr import calculate_next_review

router = APIRouter()


@router.get("/review/queue", response_model=List[ReviewResponse])
async def get_review_queue(limit: int = 20, db: Session = Depends(get_db)):
    """Get highlights that are due for review"""
    now = datetime.now()
    reviews = db.query(Review).filter(Review.next_review_at <= now).limit(limit).all()
    return reviews


@router.post("/review/answer", response_model=ReviewResponse)
async def submit_review_answer(answer: ReviewCreate, db: Session = Depends(get_db)):
    """Submit a review answer and update spaced repetition parameters"""
    # Get or create review
    review = db.query(Review).filter(Review.highlight_id == answer.highlight_id).first()
    
    if not review:
        # Create new review
        review = Review(
            highlight_id=answer.highlight_id,
            next_review_at=datetime.now(),
            interval=1,
            ease=2.5,
            reps=0
        )
        db.add(review)
    
    # Calculate new parameters
    new_ease, new_interval, new_reps, next_review_at = calculate_next_review(
        review.ease, review.interval, review.reps, answer.quality
    )
    
    # Update review
    review.ease = new_ease
    review.interval = new_interval
    review.reps = new_reps
    review.next_review_at = next_review_at
    review.last_result = answer.quality
    
    db.commit()
    db.refresh(review)
    
    return review 