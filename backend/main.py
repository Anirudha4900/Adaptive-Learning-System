
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas

from database import engine, Base, get_db


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Adaptive Learning System",
    description="Adaptive Quiz Management API",
    version="1.0.0"
)


# React frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Home API
@app.get("/")
def home():
    return {
        "message": "Adaptive Learning API is running"
    }


# Get questions based on difficulty
@app.get("/questions", response_model=list[schemas.QuestionResponse])
def get_questions(
    difficulty: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    if difficulty.lower() not in ["easy", "medium", "hard"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid difficulty level"
        )

    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 50"
        )

    questions = (
        db.query(models.Question)
        .filter(models.Question.difficulty == difficulty.lower())
        .limit(limit)
        .all()
    )

    return questions


# Save quiz result
@app.post("/quiz-attempts", response_model=schemas.QuizAttemptResponse)
def save_quiz_attempt(
    attempt: schemas.QuizAttemptCreate,
    db: Session = Depends(get_db)
):
    if attempt.total_questions <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total questions must be greater than zero"
        )

    if not 0 <= attempt.score <= attempt.total_questions:
        raise HTTPException(
            status_code=400,
            detail="Invalid score"
        )

    if not 0 <= attempt.percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid percentage"
        )

    new_attempt = models.QuizAttempt(**attempt.model_dump())

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return new_attempt


# Get quiz history
@app.get("/quiz-attempts", response_model=list[schemas.QuizAttemptResponse])
def get_quiz_history(db: Session = Depends(get_db)):
    return (
        db.query(models.QuizAttempt)
        .order_by(models.QuizAttempt.created_at.desc())
        .all()
    )

@app.post("/submit-answer", response_model=schemas.AnswerResponse)
def submit_answer(
    answer: schemas.AnswerSubmit,
    db: Session = Depends(get_db)
):
    question = (
        db.query(models.Question)
        .filter(models.Question.id == answer.question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    is_correct = (
        answer.selected_answer == question.correct_answer
    )

    return {"is_correct": is_correct}