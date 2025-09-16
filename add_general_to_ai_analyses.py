#!/usr/bin/env python3
"""
일반 분석들을 ai_analyses 테이블에 추가하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal

def add_general_analyses_to_ai():
    db = SessionLocal()
    
    try:
        # 현재 ai_analyses 테이블에 있는 분석들 확인
        result = db.execute(text("SELECT id FROM ai_analyses"))
        existing_ids = [row[0] for row in result.fetchall()]
        print(f"현재 ai_analyses 테이블에 있는 분석들: {existing_ids}")
        
        # 일반 분석들을 조회
        result = db.execute(text("SELECT id, title FROM analysis"))
        analyses = result.fetchall()
        
        print(f"\n일반 분석들:")
        for analysis_id, title in analyses:
            print(f"ID: {analysis_id}, 제목: {title}")
            
            # 이미 ai_analyses에 있지 않은 경우에만 추가
            if analysis_id not in existing_ids:
                try:
                    db.execute(text("INSERT INTO ai_analyses (id, title, description, analysis_type, created_at) VALUES (:id, :title, :description, :analysis_type, NOW())"), {
                        'id': analysis_id,
                        'title': title,
                        'description': f'{title} - AI 생성형 질문을 통한 성향 분석',
                        'analysis_type': 'general'
                    })
                    print(f"✅ {analysis_id} 추가 완료")
                except Exception as e:
                    print(f"❌ {analysis_id} 추가 실패: {e}")
            else:
                print(f"⚠️ {analysis_id} 이미 존재함")
        
        db.commit()
        print("\n모든 분석 추가 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_general_analyses_to_ai()
