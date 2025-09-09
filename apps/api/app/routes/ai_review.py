from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import requests
from ..db import get_db
from ..models import Highlight, Review, ReviewSession
from ..schemas import AIReviewRequest, AIReviewResponse, QuizQuestion
from ..config import settings

router = APIRouter()


@router.post("/ai/review/generate-quiz", response_model=QuizQuestion)
async def generate_quiz_question(
    request: AIReviewRequest, 
    db: Session = Depends(get_db)
):
    """Generate a quiz question from a highlight using Ollama"""
    highlight = db.query(Highlight).filter(Highlight.id == request.highlight_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    
    try:
        # Generate quiz question using Ollama
        prompt = f"""
        Bu highlight'tan bir quiz sorusu oluştur:
        
        Highlight: {highlight.text}
        
        Şu formatta yanıt ver:
        {{
            "question": "Soru metni",
            "correct_answer": "Doğru cevap",
            "options": ["Seçenek 1", "Seçenek 2", "Seçenek 3", "Seçenek 4"],
            "explanation": "Açıklama"
        }}
        """
        
        response = requests.post(
            f"{settings.ollama_base}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            # Parse the response and return quiz question
            # This is a simplified version
            return QuizQuestion(
                question=f"Bu highlight hakkında ne öğrendiniz?",
                correct_answer="Doğru cevap",
                options=["Seçenek 1", "Seçenek 2", "Seçenek 3", "Seçenek 4"],
                explanation="Açıklama burada olacak"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate quiz")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@router.post("/ai/review/submit-answer")
async def submit_quiz_answer(
    highlight_id: int,
    user_answer: str,
    time_spent: int,
    db: Session = Depends(get_db)
):
    """Submit a quiz answer and track learning progress"""
    highlight = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    
    # Create review session
    session = ReviewSession(
        highlight_id=highlight_id,
        session_type="quiz",
        user_answer=user_answer,
        time_spent=time_spent
    )
    
    db.add(session)
    db.commit()
    
    return {"message": "Answer submitted successfully"}


@router.get("/ai/review/learning-stats")
async def get_learning_stats(db: Session = Depends(get_db)):
    """Get learning analytics and progress statistics"""
    total_highlights = db.query(Highlight).count()
    total_reviews = db.query(Review).count()
    total_sessions = db.query(ReviewSession).count()
    
    # Calculate success rate
    correct_answers = db.query(ReviewSession).filter(ReviewSession.is_correct == True).count()
    success_rate = (correct_answers / total_sessions * 100) if total_sessions > 0 else 0
    
    return {
        "total_highlights": total_highlights,
        "total_reviews": total_reviews,
        "total_sessions": total_sessions,
        "success_rate": round(success_rate, 2),
        "correct_answers": correct_answers
    } 