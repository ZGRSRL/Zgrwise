from datetime import datetime, timedelta
from typing import Tuple


def calculate_next_review(ease: float, interval: int, reps: int, quality: int) -> Tuple[float, int, int, datetime]:
    """
    Calculate next review parameters using SM-2 algorithm
    
    Args:
        ease: Current ease factor (default 2.5, min 1.3)
        interval: Current interval in days
        reps: Number of repetitions
        quality: Quality rating (0-5)
    
    Returns:
        Tuple of (new_ease, new_interval, new_reps, next_review_at)
    """
    # Calculate new ease factor
    if quality >= 3:
        # Good response
        new_ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease = max(1.3, new_ease)  # Minimum ease factor
    else:
        # Poor response
        new_ease = max(1.3, ease - 0.2)
    
    # Calculate new interval
    if reps == 0:
        new_interval = 1
    elif reps == 1:
        new_interval = 3
    else:
        new_interval = int(ease * interval)
    
    # Calculate new repetition count
    if quality >= 3:
        new_reps = reps + 1
    else:
        new_reps = 0
    
    # Calculate next review date
    next_review_at = datetime.now() + timedelta(days=new_interval)
    
    return new_ease, new_interval, new_reps, next_review_at


def is_due_for_review(next_review_at: datetime) -> bool:
    """Check if a highlight is due for review"""
    return datetime.now() >= next_review_at 