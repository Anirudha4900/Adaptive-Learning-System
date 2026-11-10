
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


# Question Response
class QuestionResponse(BaseModel):
    id: int
    question: str
    options: List[str]
    difficulty: str
    topic: str

    model_config = ConfigDict(from_attributes=True)


# Quiz Attempt Request
class QuizAttemptCreate(BaseModel):
    difficulty: str
    score: int
    total_questions: int
    percentage: float
    topic: Optional[str] = None
    recommended_difficulty: str


# Quiz Attempt Response
class QuizAttemptResponse(QuizAttemptCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AnswerSubmit(BaseModel):
    question_id: int
    selected_answer: Optional[str] = None


class AnswerResponse(BaseModel):
    is_correct: bool