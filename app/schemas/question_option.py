from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QuestionOptionBase(BaseModel):
    """질문 선택지 기본 스키마"""
    text: str = Field(..., min_length=1, description="선택지 내용")
    value: int = Field(..., description="선택지 값")
    axis_score: float = Field(..., description="축 점수")
    order_index: int = Field(1, description="선택지 순서")


class QuestionOptionCreate(QuestionOptionBase):
    """질문 선택지 생성 스키마"""
    question_id: str = Field(..., description="질문 ID")


class QuestionOptionUpdate(BaseModel):
    """질문 선택지 업데이트 스키마"""
    text: Optional[str] = Field(None, min_length=1)
    value: Optional[int] = None
    axis_score: Optional[float] = None
    order_index: Optional[int] = None


class QuestionOptionInDB(QuestionOptionBase):
    """데이터베이스의 질문 선택지 스키마"""
    id: str
    question_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionOption(QuestionOptionInDB):
    """응답용 질문 선택지 스키마"""
    pass
