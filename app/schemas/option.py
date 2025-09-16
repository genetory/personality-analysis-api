from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OptionBase(BaseModel):
    """선택지 기본 스키마"""
    option_text: str = Field(..., min_length=1, description="선택지 내용")


class OptionCreate(OptionBase):
    """선택지 생성 스키마"""
    question_id: str = Field(..., description="질문 ID")


class OptionUpdate(BaseModel):
    """선택지 업데이트 스키마"""
    option_text: Optional[str] = Field(None, min_length=1)


class OptionInDB(OptionBase):
    """데이터베이스의 선택지 스키마"""
    id: str
    question_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Option(OptionInDB):
    """응답용 선택지 스키마"""
    pass


class OptionWithScores(Option):
    """점수가 포함된 선택지 스키마"""
    option_scores: List["OptionScore"] = []


# 순환 참조 해결을 위한 import
from app.schemas.option_score import OptionScore

# 순환 참조 해결
OptionWithScores.model_rebuild()
