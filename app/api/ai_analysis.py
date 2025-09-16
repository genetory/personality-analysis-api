from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
import json

from app.core.database import get_db
from app.services.ai_analysis_service import AIAnalysisService

router = APIRouter()

@router.post("/start")
async def start_ai_analysis(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    AI 분석 시작 - 첫 번째 질문 생성
    """
    try:
        analysis_id = request_data.get("analysis_id")
        session_id = request_data.get("session_id")
        gender = request_data.get("gender")
        
        if not all([analysis_id, session_id, gender]):
            raise HTTPException(status_code=400, detail="analysis_id, session_id, gender are required")
        
        ai_service = AIAnalysisService(db)
        result = await ai_service.start_analysis(analysis_id, session_id, gender)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer")
async def submit_answer(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    질문 답변 제출 - 다음 질문 생성 또는 분석 완료
    """
    try:
        session_id = request_data.get("session_id")
        question_id = request_data.get("question_id")
        answer = request_data.get("answer")
        gender = request_data.get("gender")
        
        if not all([session_id, question_id, answer is not None, gender]):
            raise HTTPException(status_code=400, detail="session_id, question_id, answer, gender are required")
        
        ai_service = AIAnalysisService(db)
        result = await ai_service.submit_answer(session_id, question_id, answer, gender)
        
        return result
        
    except Exception as e:
        print(f"submit_answer API 에러: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    AI 분석 서비스 상태 확인
    """
    return {"status": "healthy", "service": "ai_analysis"}