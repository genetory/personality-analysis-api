from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisBase(BaseModel):
    """성향분석 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=255, description="성향분석 제목")
    description: Optional[str] = Field(None, description="성향분석 설명")
    total_questions: str = Field("0", description="총 질문 수")
    result_type: str = Field(..., description="결과 타입 (binary_pairs, continuous, categories, custom)")
    result_config: Optional[Dict[str, Any]] = Field(None, description="결과 해석 규칙")


class AnalysisCreate(AnalysisBase):
    """성향분석 생성 스키마"""
    pass


class AnalysisUpdate(BaseModel):
    """성향분석 업데이트 스키마"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    total_questions: Optional[str] = None
    result_type: Optional[str] = None
    result_config: Optional[Dict[str, Any]] = None


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
    dimensions: List["Dimension"] = []
    questions: List["Question"] = []


# 순환 참조 해결을 위한 import
from app.schemas.dimension import Dimension
from app.schemas.question import Question

# 순환 참조 해결
AnalysisWithDetails.model_rebuild()
