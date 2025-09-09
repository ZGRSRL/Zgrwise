"""
AI utilities for ZgrWise
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def summarize_text(text: str) -> str:
    """Simple text summarization - just return first 200 chars"""
    if len(text) <= 200:
        return text
    return text[:200] + "..."


def generate_tags(text: str) -> list:
    """Simple tag generation - return empty list for now"""
    return []


def generate_quiz_question(highlight_text: str) -> dict:
    """Generate a simple quiz question"""
    return {
        "question": f"What is the main point of: '{highlight_text[:50]}...'?",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer": "Option 1",
        "explanation": "This is a simple explanation."
    }


def generate_summary(text: str) -> str:
    """Generate summary - alias for summarize_text"""
    return summarize_text(text)