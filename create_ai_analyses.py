#!/usr/bin/env python3
"""
AI 분석 데이터 생성 스크립트
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.ai_analysis import AIAnalysis
import uuid

def create_ai_analyses():
    """AI 분석 데이터 생성"""
    db = SessionLocal()
    
    try:
        # 에겐/테토 분석 생성
        egen_teto_analysis = AIAnalysis(
            id="c9d398d0-8d65-11f0-ab6e-4177906e770b",
            title="에겐/테토 성향 분석",
            description="당신의 독특한 성향을 분석해드립니다. 에겐과 테토 중 어떤 성향일까요?",
            analysis_type="egen_teto",
            is_active=1
        )
        
        # BDSM 분석 생성
        bdsm_analysis = AIAnalysis(
            id="bdsm-analysis",
            title="BDSM 성향 분석",
            description="파트너와의 관계에서 당신의 성향을 분석해드립니다. 도미넌트, 서브, 스위치 중 어떤 성향일까요?",
            analysis_type="bdsm",
            is_active=1
        )
        
        # 기존 데이터 삭제 후 삽입
        db.query(AIAnalysis).delete()
        
        db.add(egen_teto_analysis)
        db.add(bdsm_analysis)
        
        db.commit()
        print("AI 분석 데이터가 성공적으로 생성되었습니다!")
        print(f"- 에겐/테토 분석: {egen_teto_analysis.id}")
        print(f"- BDSM 분석: {bdsm_analysis.id}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_ai_analyses()
