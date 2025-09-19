from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    """질문 기본 스키마"""
    text: str = Field(..., min_length=1, description="질문 내용")
    category: str = Field(..., description="질문 카테고리")
    axis: str = Field(..., description="성향 축")
    order_index: int = Field(1, description="질문 순서")


class QuestionCreate(QuestionBase):
    """질문 생성 스키마"""
    analysis_type_id: str = Field(..., description="분석 유형 ID")


class QuestionUpdate(BaseModel):
    """질문 업데이트 스키마"""
    text: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    axis: Optional[str] = None
    order_index: Optional[int] = None


class QuestionInDB(QuestionBase):
    """데이터베이스의 질문 스키마"""
    id: str
    analysis_type_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Question(QuestionInDB):
    """응답용 질문 스키마"""
    pass


class QuestionWithOptions(Question):
    """선택지가 포함된 질문 스키마"""
    options: List["QuestionOption"] = []


# 순환 참조 해결을 위한 import
from app.schemas.question_option import QuestionOption

# 순환 참조 해결
QuestionWithOptions.model_rebuild()
