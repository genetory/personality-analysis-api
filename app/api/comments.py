from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.comment_service import CommentService
from app.schemas.comment import Comment, CommentCreate, CommentUpdate, CommentListResponse

router = APIRouter()


@router.post("/", response_model=Comment)
def create_comment(comment_data: CommentCreate, db: Session = Depends(get_db)):
    """댓글 작성"""
    service = CommentService(db)
    return service.create_comment(comment_data)


@router.get("/analysis/{analysis_id}", response_model=CommentListResponse)
def get_comments_by_analysis(
    analysis_id: str,
    sort_by: str = Query("latest", description="정렬 기준: latest(최신순), popular(인기순)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=50, description="페이지당 댓글 수"),
    db: Session = Depends(get_db)
):
    """분석별 댓글 조회 (정렬, 페이지네이션)"""
    service = CommentService(db)
    result = service.get_comments_by_analysis(analysis_id, sort_by, page, per_page)
    
    return CommentListResponse(
        comments=result["comments"],
        total_count=result["total_count"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"]
    )


@router.get("/{comment_id}", response_model=Comment)
def get_comment(comment_id: str, db: Session = Depends(get_db)):
    """댓글 상세 조회"""
    service = CommentService(db)
    comment = service.get_comment_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    return comment


@router.put("/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: str, 
    comment_data: CommentUpdate, 
    db: Session = Depends(get_db)
):
    """댓글 수정"""
    service = CommentService(db)
    comment = service.update_comment(comment_id, comment_data)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    return comment


@router.delete("/{comment_id}")
def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    """댓글 삭제"""
    service = CommentService(db)
    success = service.delete_comment(comment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    return {"message": "댓글이 삭제되었습니다."}


@router.post("/{comment_id}/like", response_model=Comment)
def like_comment(comment_id: str, db: Session = Depends(get_db)):
    """댓글 좋아요"""
    service = CommentService(db)
    comment = service.like_comment(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    return comment


@router.get("/analysis/{analysis_id}/stats")
def get_analysis_comment_stats(analysis_id: str, db: Session = Depends(get_db)):
    """분석별 댓글 통계"""
    service = CommentService(db)
    return service.get_analysis_stats(analysis_id)
