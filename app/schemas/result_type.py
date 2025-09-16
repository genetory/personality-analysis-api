from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResultInterpretationBase(BaseModel):
    """결과 해석 기본 스키마"""
    section: str = Field(..., description="해석 섹션 (성격 특징, 인간관계, 연애 스타일 등)")
    content: str = Field(..., description="해석 내용")


class ResultInterpretation(ResultInterpretationBase):
    """결과 해석 응답 스키마"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResultTypeBase(BaseModel):
    """결과 타입 기본 스키마"""
    result_key: str = Field(..., description="결과 키 (예: 액티브-테토-플로우)")
    title: str = Field(..., description="결과 제목 (예: 솔직한 해결사)")
    subtitle: Optional[str] = Field(None, description="결과 부제 (예: 문제 터지면 제일 먼저 달려가는 급발진 해결 담당)")
    gender: str = Field(..., description="성별 (male, female)")


class ResultTypeCreate(ResultTypeBase):
    """결과 타입 생성 스키마"""
    analysis_id: str = Field(..., description="분석 ID")


class ResultType(ResultTypeBase):
    """결과 타입 응답 스키마"""
    id: str
    analysis_id: str
    created_at: datetime
    interpretations: List[ResultInterpretation] = []
    
    class Config:
        from_attributes = True


class ResultTypeWithInterpretations(ResultType):
    """해석이 포함된 결과 타입 스키마"""
    interpretations: List[ResultInterpretation] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """해석을 딕셔너리 형태로 변환"""
        result = {
            "id": self.id,
            "result_key": self.result_key,
            "title": self.title,
            "subtitle": self.subtitle,
            "gender": self.gender,
            "interpretations": {}
        }
        
        for interpretation in self.interpretations:
            result["interpretations"][interpretation.section] = interpretation.content
            
        return result
