from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResponseBase(BaseModel):
    """응답 기본 스키마"""
    session_id: str = Field(..., min_length=1, description="세션 ID")
    question_id: str = Field(..., description="질문 ID")
    option_id: str = Field(..., description="선택지 ID")
    gender: Optional[str] = Field(None, description="성별 (male/female)")


class ResponseCreate(ResponseBase):
    """응답 생성 스키마"""
    pass


class ResponseUpdate(BaseModel):
    """응답 업데이트 스키마"""
    option_id: Optional[str] = None


class ResponseInDB(ResponseBase):
    """데이터베이스의 응답 스키마"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Response(ResponseInDB):
    """응답용 응답 스키마"""
    pass


class ResponseBatch(BaseModel):
    """배치 응답 스키마"""
    session_id: str = Field(..., min_length=1, description="세션 ID")
    gender: str = Field(..., description="성별 (male/female)")
    responses: list[dict] = Field(..., description="응답 목록 [{'question_id': str, 'option_id': str}]")
