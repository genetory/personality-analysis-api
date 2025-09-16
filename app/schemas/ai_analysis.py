from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AIAnalysisSessionCreate(BaseModel):
    analysis_id: str
    session_id: str
    gender: str = "male"  # 'male', 'female'

class AIAnalysisSessionResponse(BaseModel):
    id: str
    analysis_id: str
    session_id: str
    gender: str
    status: str
    current_question_index: int
    answers: List[Dict[str, Any]]
    result_type: Optional[str]
    result_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AIQuestionResponse(BaseModel):
    question_id: str
    question_text: str
    option_1: str
    option_2: str
    question_index: int
    total_questions: int

class AIAnswerRequest(BaseModel):
    question_id: str
    answer: int  # 1 or 2

class AIAnalysisResultResponse(BaseModel):
    result_type: str
    title: str
    description: str
    characteristics: List[str]
    compatibility: Dict[str, str]
    recommendations: List[str]
    confidence_score: int
