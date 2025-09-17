from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisBase(BaseModel):
    """성향분석 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="성향분석 이름")
    description: str = Field(..., description="성향분석 설명")
    category: str = Field(..., description="성향분석 카테고리")
    participants: int = Field(0, description="참여자 수")
    thumb_image_url: Optional[str] = Field(None, description="썸네일 이미지 URL")
    is_active: int = Field(1, description="활성화 상태")


class AnalysisCreate(AnalysisBase):
    """성향분석 생성 스키마"""
    pass


class AnalysisUpdate(BaseModel):
    """성향분석 업데이트 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    participants: Optional[int] = None
    thumb_image_url: Optional[str] = None
    is_active: Optional[int] = None


class AnalysisInDB(AnalysisBase):
    """데이터베이스의 성향분석 스키마"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Analysis(AnalysisInDB):
    """응답용 성향분석 스키마"""
    pass


class AnalysisWithDetails(Analysis):
    """상세 정보가 포함된 성향분석 스키마"""
    questions: List["Question"] = []


# 순환 참조 해결을 위한 import
from app.schemas.question import Question

# 순환 참조 해결
AnalysisWithDetails.model_rebuild()
