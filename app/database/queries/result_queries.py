from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.models.database import AnalysisResult, Answer, Question, AnalysisType, User
from app.core.database import SessionLocal
from datetime import datetime, timedelta

class ResultQueries:
    """분석 결과 관련 데이터베이스 쿼리 클래스"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    # 기본 CRUD 작업
    def get_result_by_id(self, result_id: str) -> Optional[AnalysisResult]:
        """ID로 분석 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    
    def get_results_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """특정 사용자의 모든 분석 결과를 조회합니다. (user_id가 None이면 익명 사용자 결과 조회)"""
        if user_id is None:
            # 익명 사용자 결과 조회 (user_id가 NULL인 결과들)
            return self.db.query(AnalysisResult).filter(
                AnalysisResult.user_id.is_(None)
            ).order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
        else:
            # 특정 사용자 결과 조회
            return self.db.query(AnalysisResult).filter(
                AnalysisResult.user_id == user_id
            ).order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
    
    def get_all_results(self, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """모든 분석 결과를 조회합니다."""
        return self.db.query(AnalysisResult).order_by(
            desc(AnalysisResult.created_at)
        ).offset(skip).limit(limit).all()
    
    def delete_result(self, result_id: str) -> bool:
        """분석 결과를 삭제합니다."""
        result = self.get_result_by_id(result_id)
        if result:
            self.db.delete(result)
            self.db.commit()
            return True
        return False
    
    # 통계 및 분석 쿼리
    def get_result_statistics(self) -> Dict[str, Any]:
        """분석 결과 통계를 조회합니다."""
        total_results = self.db.query(AnalysisResult).count()
        total_users = self.db.query(User).count()
        
        # 최근 30일간의 결과 수
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_results = self.db.query(AnalysisResult).filter(
            AnalysisResult.created_at >= thirty_days_ago
        ).count()
        
        # 가장 인기 있는 성격 유형
        popular_types = self.db.query(
            AnalysisResult.personality_type,
            func.count(AnalysisResult.id).label('count')
        ).group_by(AnalysisResult.personality_type).order_by(
            desc('count')
        ).limit(5).all()
        
        return {
            "total_results": total_results,
            "total_users": total_users,
            "recent_results": recent_results,
            "popular_personality_types": [
                {"type": pt.personality_type, "count": pt.count} 
                for pt in popular_types
            ]
        }
    
    def get_results_by_analysis_type(self, analysis_type_id: str, 
                                   skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """특정 성향분석 유형의 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.analysis_type_id == analysis_type_id
        ).order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
    
    def get_results_by_date_range(self, start_date: datetime, end_date: datetime,
                                skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """날짜 범위로 분석 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.created_at >= start_date,
            AnalysisResult.created_at <= end_date
        ).order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
    
    def get_results_by_personality_type(self, personality_type: str,
                                      skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """특정 성격 유형의 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.personality_type == personality_type
        ).order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
    
    # 점수 기반 쿼리
    def get_results_by_score_range(self, axis: str, min_score: float, max_score: float,
                                 skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """특정 축의 점수 범위로 결과를 조회합니다."""
        if axis == "empathy":
            query = self.db.query(AnalysisResult).filter(
                AnalysisResult.empathy_score >= min_score,
                AnalysisResult.empathy_score <= max_score
            )
        elif axis == "active":
            query = self.db.query(AnalysisResult).filter(
                AnalysisResult.active_score >= min_score,
                AnalysisResult.active_score <= max_score
            )
        elif axis == "plan":
            query = self.db.query(AnalysisResult).filter(
                AnalysisResult.plan_score >= min_score,
                AnalysisResult.plan_score <= max_score
            )
        elif axis == "express":
            query = self.db.query(AnalysisResult).filter(
                AnalysisResult.express_score >= min_score,
                AnalysisResult.express_score <= max_score
            )
        else:
            return []
        
        return query.order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
    
    def get_average_scores_by_analysis_type(self, analysis_type_id: str) -> Dict[str, float]:
        """특정 성향분석 유형의 평균 점수를 조회합니다."""
        result = self.db.query(
            func.avg(AnalysisResult.empathy_score).label('avg_empathy'),
            func.avg(AnalysisResult.active_score).label('avg_active'),
            func.avg(AnalysisResult.plan_score).label('avg_plan'),
            func.avg(AnalysisResult.express_score).label('avg_express')
        ).filter(AnalysisResult.analysis_type_id == analysis_type_id).first()
        
        if result:
            return {
                "empathy": float(result.avg_empathy or 0),
                "active": float(result.avg_active or 0),
                "plan": float(result.avg_plan or 0),
                "express": float(result.avg_express or 0)
            }
        return {"empathy": 0, "active": 0, "plan": 0, "express": 0}
    
    # 복합 쿼리
    def get_detailed_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """분석 결과와 관련된 모든 정보를 조회합니다."""
        result = self.db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
        if not result:
            return None
        
        # 관련 정보 조회
        analysis_type = self.db.query(AnalysisType).filter(
            AnalysisType.id == result.analysis_type_id
        ).first()
        
        user = None
        if result.user_id:
            user = self.db.query(User).filter(User.id == result.user_id).first()
        
        answers = self.db.query(Answer).filter(
            Answer.analysis_result_id == result_id
        ).all()
        
        return {
            "result": result,
            "analysis_type": analysis_type,
            "user": user,
            "answers": answers
        }
    
    def search_results(self, query: str, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """분석 결과를 검색합니다 (성격 유형, 설명)."""
        return self.db.query(AnalysisResult).filter(
            (AnalysisResult.personality_type.contains(query)) |
            (AnalysisResult.description.contains(query))
        ).order_by(desc(AnalysisResult.created_at)).offset(skip).limit(limit).all()
    
    def get_user_result_count(self, user_id: str) -> int:
        """특정 사용자의 분석 결과 수를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.user_id == user_id
        ).count()
    
    def get_anonymous_result_count(self) -> int:
        """익명 사용자의 분석 결과 수를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.user_id.is_(None)
        ).count()
    
    def get_anonymous_results_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AnalysisResult]:
        """날짜 범위로 익명 사용자 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.user_id.is_(None),
            AnalysisResult.created_at >= start_date,
            AnalysisResult.created_at <= end_date
        ).order_by(desc(AnalysisResult.created_at)).all()
    
    def get_latest_result_by_user(self, user_id: str) -> Optional[AnalysisResult]:
        """특정 사용자의 최신 분석 결과를 조회합니다."""
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.user_id == user_id
        ).order_by(desc(AnalysisResult.created_at)).first()
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        if self.db:
            self.db.close()
