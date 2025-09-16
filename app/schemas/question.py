from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    """질문 기본 스키마"""
    question_text: str = Field(..., min_length=1, description="질문 내용")
    question_order: str = Field("1", description="질문 순서")


class QuestionCreate(QuestionBase):
    """질문 생성 스키마"""
    analysis_id: str = Field(..., description="분석 ID")


class QuestionUpdate(BaseModel):
    """질문 업데이트 스키마"""
    question_text: Optional[str] = Field(None, min_length=1)
    question_order: Optional[str] = None


class QuestionInDB(QuestionBase):
    """데이터베이스의 질문 스키마"""
    id: str
    analysis_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Question(QuestionInDB):
    """응답용 질문 스키마"""
    pass


class QuestionWithOptions(Question):
    """선택지가 포함된 질문 스키마"""
    options: List["Option"] = []


# 순환 참조 해결을 위한 import
from app.schemas.option import Option

# 순환 참조 해결
QuestionWithOptions.model_rebuild()
