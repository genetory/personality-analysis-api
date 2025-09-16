#!/usr/bin/env python3
"""
일반 분석들을 AI 분석으로 등록하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.analysis import Analysis

def create_ai_analyses():
    db = SessionLocal()
    
    try:
        # 모든 분석 조회
        analyses = db.query(Analysis).all()
        
        print(f"총 {len(analyses)}개의 분석을 찾았습니다.")
        
        for analysis in analyses:
            ai_analysis_id = f"ai-{analysis.id}-analysis"
            print(f"분석 ID: {analysis.id}, 제목: {analysis.title}")
            print(f"AI 분석 ID: {ai_analysis_id}")
            print("---")
        
        print("\n이 스크립트는 분석 목록을 보여주기 위한 것입니다.")
        print("실제 AI 분석 등록은 별도의 테이블이나 설정이 필요합니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_ai_analyses()
