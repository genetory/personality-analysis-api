from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OptionScoreBase(BaseModel):
    """선택지 점수 기본 스키마"""
    score_value: float = Field(..., description="점수 값")


class OptionScoreCreate(OptionScoreBase):
    """선택지 점수 생성 스키마"""
    option_id: str = Field(..., description="선택지 ID")
    dimension_id: str = Field(..., description="차원 ID")


class OptionScoreUpdate(BaseModel):
    """선택지 점수 업데이트 스키마"""
    score_value: Optional[float] = None


class OptionScoreInDB(OptionScoreBase):
    """데이터베이스의 선택지 점수 스키마"""
    id: str
    option_id: str
    dimension_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OptionScore(OptionScoreInDB):
    """응답용 선택지 점수 스키마"""
    pass
