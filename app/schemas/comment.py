from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CommentBase(BaseModel):
    """댓글 기본 스키마"""
    nickname: str = Field(..., min_length=1, max_length=50, description="닉네임")
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")
    rating: Optional[int] = Field(None, ge=1, le=5, description="별점 (1-5)")


class CommentCreate(CommentBase):
    """댓글 생성 스키마"""
    analysis_id: str = Field(..., description="분석 ID")


class CommentUpdate(BaseModel):
    """댓글 수정 스키마"""
    content: Optional[str] = Field(None, min_length=1, max_length=1000, description="댓글 내용")
    rating: Optional[int] = Field(None, ge=1, le=5, description="별점 (1-5)")


class Comment(CommentBase):
    """댓글 응답 스키마"""
    id: str = Field(..., description="댓글 ID")
    analysis_id: str = Field(..., description="분석 ID")
    likes: int = Field(0, description="좋아요 수")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """댓글 목록 응답 스키마"""
    comments: List[Comment] = Field(..., description="댓글 목록")
    total_count: int = Field(..., description="전체 댓글 수")
    page: int = Field(..., description="현재 페이지")
    per_page: int = Field(..., description="페이지당 댓글 수")
    total_pages: int = Field(..., description="전체 페이지 수")
