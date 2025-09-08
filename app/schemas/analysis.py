from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class AnalysisTypeResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    participants: int
    thumb_image_url: Optional[str]
    is_active: int
    created_at: datetime
    updated_at: datetime

class QuestionResponse(BaseModel):
    id: str
    analysis_type_id: str
    text: str
    category: str
    axis: str
    order_index: int
    created_at: datetime

class QuestionOptionResponse(BaseModel):
    id: str
    question_id: str
    text: str
    value: int
    axis_score: float
    order_index: int
    created_at: datetime

class AnalysisResultResponse(BaseModel):
    id: str
    user_id: Optional[str]
    analysis_type_id: str
    empathy_score: float
    active_score: float
    plan_score: float
    express_score: float
    personality_type: str
    description: str
    recommendations: Optional[List[str]]
    created_at: datetime

class AnswerResponse(BaseModel):
    id: str
    analysis_result_id: str
    question_id: str
    question_option_id: str
    value: int

class AnalyzeRequest(BaseModel):
    analysis_type_id: str
    answers: List[dict]
    user_id: Optional[str] = None

class AnalyzeResponse(BaseModel):
    result: AnalysisResultResponse
    message: str
