from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
import math


class CommentService:
    """댓글 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_comment(self, comment_data: CommentCreate) -> Comment:
        """댓글 생성"""
        db_comment = Comment(**comment_data.model_dump())
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_comments_by_analysis(
        self, 
        analysis_id: str, 
        sort_by: str = "latest", 
        page: int = 1, 
        per_page: int = 10
    ) -> dict:
        """분석별 댓글 조회 (정렬, 페이지네이션)"""
        # 정렬 기준 설정
        if sort_by == "popular":
            order_by = desc(Comment.likes)
        else:  # latest
            order_by = desc(Comment.created_at)
        
        # 전체 댓글 수 조회
        total_count = self.db.query(Comment).filter(Comment.analysis_id == analysis_id).count()
        
        # 페이지네이션 계산
        offset = (page - 1) * per_page
        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
        
        # 댓글 조회
        comments = (
            self.db.query(Comment)
            .filter(Comment.analysis_id == analysis_id)
            .order_by(order_by)
            .offset(offset)
            .limit(per_page)
            .all()
        )
        
        return {
            "comments": comments,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """댓글 ID로 조회"""
        return self.db.query(Comment).filter(Comment.id == comment_id).first()
    
    def update_comment(self, comment_id: str, comment_data: CommentUpdate) -> Optional[Comment]:
        """댓글 수정"""
        db_comment = self.get_comment_by_id(comment_id)
        if not db_comment:
            return None
        
        update_data = comment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)
        
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def delete_comment(self, comment_id: str) -> bool:
        """댓글 삭제"""
        db_comment = self.get_comment_by_id(comment_id)
        if not db_comment:
            return False
        
        self.db.delete(db_comment)
        self.db.commit()
        return True
    
    def like_comment(self, comment_id: str) -> Optional[Comment]:
        """댓글 좋아요"""
        db_comment = self.get_comment_by_id(comment_id)
        if not db_comment:
            return None
        
        db_comment.likes += 1
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_analysis_stats(self, analysis_id: str) -> dict:
        """분석별 댓글 통계"""
        comments = self.db.query(Comment).filter(Comment.analysis_id == analysis_id).all()
        
        if not comments:
            return {
                "total_comments": 0,
                "average_rating": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        # 평균 별점 계산
        rated_comments = [c for c in comments if c.rating is not None]
        average_rating = sum(c.rating for c in rated_comments) / len(rated_comments) if rated_comments else 0
        
        # 별점 분포 계산
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for comment in rated_comments:
            rating_distribution[comment.rating] += 1
        
        return {
            "total_comments": len(comments),
            "average_rating": round(average_rating, 1),
            "rating_distribution": rating_distribution
        }
