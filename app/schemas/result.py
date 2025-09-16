from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ResultBase(BaseModel):
    """결과 기본 스키마"""
    session_id: str = Field(..., min_length=1, description="세션 ID")
    analysis_id: str = Field(..., description="분석 ID")
    dimension_scores: Dict[str, float] = Field(..., description="각 성향 차원별 점수")
    result_data: Optional[Dict[str, Any]] = Field(None, description="최종 결과 데이터")


class ResultCreate(ResultBase):
    """결과 생성 스키마"""
    pass


class ResultUpdate(BaseModel):
    """결과 업데이트 스키마"""
    dimension_scores: Optional[Dict[str, float]] = None
    result_data: Optional[Dict[str, Any]] = None


class ResultInDB(ResultBase):
    """데이터베이스의 결과 스키마"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Result(ResultInDB):
    """응답용 결과 스키마"""
    pass


class ResultWithAnalysis(Result):
    """분석 정보가 포함된 결과 스키마"""
    analysis: Optional["Analysis"] = None


class UserResult(BaseModel):
    """사용자용 간소화된 결과 스키마"""
    result_type: str = Field(..., description="결과 유형")
    label: str = Field(..., description="결과 라벨")
    interpretation: str = Field(..., description="기본 해석")
    detailed_interpretation: str = Field(..., description="상세 해석")
    gender: Optional[str] = Field(None, description="성별")


# 순환 참조 해결을 위한 import
from app.schemas.analysis import Analysis

# 순환 참조 해결
ResultWithAnalysis.model_rebuild()
