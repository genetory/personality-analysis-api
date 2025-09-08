from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuestionBase(BaseModel):
    id: int
    text: str
    category: str
    reverse: Optional[bool] = False

class Question(QuestionBase):
    pass

class AnswerBase(BaseModel):
    question_id: int
    value: int  # 1-5 scale

class Answer(AnswerBase):
    pass

class AnalysisRequest(BaseModel):
    answers: List[Answer]
    user_id: Optional[str] = None

class PersonalityScores(BaseModel):
    extroversion: float
    openness: float
    conscientiousness: float
    agreeableness: float
    neuroticism: float

class AnalysisResult(BaseModel):
    id: str
    user_id: Optional[str]
    scores: PersonalityScores
    personality_type: str
    description: str
    recommendations: List[str]
    created_at: datetime

class AnalysisResponse(BaseModel):
    success: bool
    result: Optional[AnalysisResult] = None
    message: Optional[str] = None

class PopularAnalysis(BaseModel):
    id: int
    name: str
    description: str
    category: str
    participants: int
    color: str
    bg_color: str

class AnalysisListResponse(BaseModel):
    success: bool
    analyses: List[PopularAnalysis]
    total: int
