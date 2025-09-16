from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DimensionBase(BaseModel):
    """성향 차원 기본 스키마"""
    dimension_name: str = Field(..., min_length=1, max_length=100, description="차원 이름")
    dimension_description: Optional[str] = Field(None, description="차원 설명")
    dimension_type: str = Field(..., description="차원 타입 (binary, continuous, category)")
    min_value: Optional[float] = Field(None, description="최소값 (연속형용)")
    max_value: Optional[float] = Field(None, description="최대값 (연속형용)")


class DimensionCreate(DimensionBase):
    """성향 차원 생성 스키마"""
    analysis_id: str = Field(..., description="분석 ID")


class DimensionUpdate(BaseModel):
    """성향 차원 업데이트 스키마"""
    dimension_name: Optional[str] = Field(None, min_length=1, max_length=100)
    dimension_description: Optional[str] = None
    dimension_type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class DimensionInDB(DimensionBase):
    """데이터베이스의 성향 차원 스키마"""
    id: str
    analysis_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Dimension(DimensionInDB):
    """응답용 성향 차원 스키마"""
    pass
