from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.database.queries import AnalysisQueries, UserQueries, ResultQueries

class QueryManager:
    """데이터베이스 쿼리 통합 관리 클래스"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.analysis = AnalysisQueries(self.db)
        self.user = UserQueries(self.db)
        self.result = ResultQueries(self.db)
    
    def get_analysis_queries(self) -> AnalysisQueries:
        """성향분석 관련 쿼리를 반환합니다."""
        return self.analysis
    
    def get_user_queries(self) -> UserQueries:
        """사용자 관련 쿼리를 반환합니다."""
        return self.user
    
    def get_result_queries(self) -> ResultQueries:
        """결과 관련 쿼리를 반환합니다."""
        return self.result
    
    def close(self):
        """모든 데이터베이스 연결을 종료합니다."""
        self.analysis.close()
        self.user.close()
        self.result.close()
        if self.db:
            self.db.close()
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()

# 전역 쿼리 매니저 인스턴스
query_manager = QueryManager()
