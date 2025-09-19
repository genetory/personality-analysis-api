from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, asc
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, Comment as CommentSchema, CommentListResponse

router = APIRouter()


@router.post("/comments/", response_model=CommentSchema)
async def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """댓글 생성"""
    try:
        # 분석 ID 존재 확인
        analysis_check = db.execute(text("SELECT id FROM analysis_types WHERE id = :analysis_id"), 
                                  {"analysis_id": comment.analysis_id}).fetchone()
        if not analysis_check:
            raise HTTPException(status_code=404, detail="분석을 찾을 수 없습니다.")
        
        # 댓글 생성
        db_comment = Comment(
            id=str(uuid.uuid4()),
            analysis_id=comment.analysis_id,
            nickname=comment.nickname,
            content=comment.content,
            rating=comment.rating,
            likes=0
        )
        
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        
        return db_comment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"댓글 생성 실패: {str(e)}")


@router.get("/comments/analysis/{analysis_id}", response_model=CommentListResponse)
async def get_comments(
    analysis_id: str,
    sort_by: str = Query("latest", description="정렬 기준: latest(최신순), popular(인기순)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=50, description="페이지당 댓글 수"),
    db: Session = Depends(get_db)
):
    """분석별 댓글 목록 조회"""
    try:
        # 분석 ID 존재 확인
        analysis_check = db.execute(text("SELECT id FROM analysis_types WHERE id = :analysis_id"), 
                                  {"analysis_id": analysis_id}).fetchone()
        if not analysis_check:
            raise HTTPException(status_code=404, detail="분석을 찾을 수 없습니다.")
        
        # 정렬 기준 설정
        if sort_by == "popular":
            order_by = desc(Comment.likes), desc(Comment.created_at)
        else:  # latest
            order_by = desc(Comment.created_at)
        
        # 전체 댓글 수 조회
        total_count_query = text("SELECT COUNT(*) FROM comments WHERE analysis_id = :analysis_id")
        total_count = db.execute(total_count_query, {"analysis_id": analysis_id}).scalar()
        
        # 페이지네이션 계산
        total_pages = (total_count + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # 댓글 목록 조회
        comments_query = text("""
            SELECT id, analysis_id, nickname, content, rating, likes, created_at, updated_at
            FROM comments 
            WHERE analysis_id = :analysis_id
            ORDER BY 
                CASE WHEN :sort_by = 'popular' THEN likes END DESC,
                CASE WHEN :sort_by = 'popular' THEN created_at END DESC,
                CASE WHEN :sort_by = 'latest' THEN created_at END DESC
            LIMIT :per_page OFFSET :offset
        """)
        
        comments_result = db.execute(comments_query, {
            "analysis_id": analysis_id,
            "sort_by": sort_by,
            "per_page": per_page,
            "offset": offset
        }).fetchall()
        
        # 결과 변환
        comments = []
        for row in comments_result:
            comments.append(CommentSchema(
                id=row[0],
                analysis_id=row[1],
                nickname=row[2],
                content=row[3],
                rating=row[4],
                likes=row[5],
                created_at=row[6],
                updated_at=row[7]
            ))
        
        return CommentListResponse(
            comments=comments,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"댓글 조회 실패: {str(e)}")


@router.post("/comments/{comment_id}/like")
async def like_comment(comment_id: str, db: Session = Depends(get_db)):
    """댓글 좋아요"""
    try:
        # 댓글 존재 확인 및 좋아요 수 증가
        result = db.execute(text("""
            UPDATE comments 
            SET likes = likes + 1 
            WHERE id = :comment_id
        """), {"comment_id": comment_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
        
        db.commit()
        
        return {"message": "좋아요가 추가되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"좋아요 실패: {str(e)}")


@router.put("/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
    comment_id: str, 
    comment_update: CommentUpdate, 
    db: Session = Depends(get_db)
):
    """댓글 수정"""
    try:
        # 댓글 존재 확인
        comment = db.execute(text("""
            SELECT id, analysis_id, nickname, content, rating, likes, created_at, updated_at
            FROM comments 
            WHERE id = :comment_id
        """), {"comment_id": comment_id}).fetchone()
        
        if not comment:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
        
        # 댓글 수정
        update_fields = []
        update_values = {"comment_id": comment_id}
        
        if comment_update.content is not None:
            update_fields.append("content = :content")
            update_values["content"] = comment_update.content
            
        if comment_update.rating is not None:
            update_fields.append("rating = :rating")
            update_values["rating"] = comment_update.rating
        
        if update_fields:
            update_query = text(f"""
                UPDATE comments 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = :comment_id
            """)
            
            db.execute(update_query, update_values)
            db.commit()
        
        # 수정된 댓글 조회
        updated_comment = db.execute(text("""
            SELECT id, analysis_id, nickname, content, rating, likes, created_at, updated_at
            FROM comments 
            WHERE id = :comment_id
        """), {"comment_id": comment_id}).fetchone()
        
        return CommentSchema(
            id=updated_comment[0],
            analysis_id=updated_comment[1],
            nickname=updated_comment[2],
            content=updated_comment[3],
            rating=updated_comment[4],
            likes=updated_comment[5],
            created_at=updated_comment[6],
            updated_at=updated_comment[7]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"댓글 수정 실패: {str(e)}")


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    """댓글 삭제"""
    try:
        # 댓글 존재 확인 및 삭제
        result = db.execute(text("DELETE FROM comments WHERE id = :comment_id"), 
                          {"comment_id": comment_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
        
        db.commit()
        
        return {"message": "댓글이 삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"댓글 삭제 실패: {str(e)}")
