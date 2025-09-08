from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.response import ApiResponse, SuccessResponse, ErrorResponse
from app.schemas.analysis import (
    AnalysisTypeResponse, QuestionResponse, QuestionOptionResponse, 
    AnalysisResultResponse, AnalyzeRequest, AnalyzeResponse
)
from app.services.analysis_service import AnalysisService

router = APIRouter()

# 성향분석 서비스 인스턴스
analysis_service = AnalysisService()

@router.get("/types", response_model=ApiResponse)
async def get_analysis_types():
    """성향분석 유형 목록을 반환합니다."""
    try:
        analysis_types = analysis_service.get_analysis_types()
        # SQLAlchemy 모델을 Pydantic 스키마로 변환
        response_data = [
            AnalysisTypeResponse(
                id=at.id,
                name=at.name,
                description=at.description,
                category=at.category,
                participants=at.participants,
                thumb_image_url=at.thumb_image_url,
                is_active=at.is_active,
                created_at=at.created_at,
                updated_at=at.updated_at
            ) for at in analysis_types
        ]
        return SuccessResponse(
            data=response_data,
            message="성향분석 유형 목록을 성공적으로 조회했습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"성향분석 유형 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.get("/types/{analysis_type_id}/questions", response_model=ApiResponse)
async def get_questions_by_type(analysis_type_id: str):
    """특정 성향분석 유형의 질문 목록을 반환합니다."""
    try:
        questions = analysis_service.get_questions_by_analysis_type(analysis_type_id)
        # SQLAlchemy 모델을 Pydantic 스키마로 변환
        response_data = [
            QuestionResponse(
                id=q.id,
                analysis_type_id=q.analysis_type_id,
                text=q.text,
                category=q.category,
                axis=q.axis,
                order_index=q.order_index,
                created_at=q.created_at
            ) for q in questions
        ]
        return SuccessResponse(
            data=response_data,
            message="질문 목록을 성공적으로 조회했습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"질문 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.get("/questions/{question_id}/options", response_model=ApiResponse)
async def get_question_options(question_id: str):
    """특정 질문의 선택지 목록을 반환합니다."""
    try:
        options = analysis_service.get_question_options(question_id)
        # SQLAlchemy 모델을 Pydantic 스키마로 변환
        response_data = [
            QuestionOptionResponse(
                id=opt.id,
                question_id=opt.question_id,
                text=opt.text,
                value=opt.value,
                axis_score=opt.axis_score,
                order_index=opt.order_index,
                created_at=opt.created_at
            ) for opt in options
        ]
        return SuccessResponse(
            data=response_data,
            message="선택지 목록을 성공적으로 조회했습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"선택지 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.post("/analyze", response_model=ApiResponse)
async def analyze_personality(analysis_type_id: str, answers: List[dict], user_id: str = None):
    """사용자의 답변을 바탕으로 성향분석을 수행합니다. (익명 사용자 지원)"""
    try:
        # 답변 검증
        if not answers:
            return ErrorResponse(
                message="답변이 필요합니다.",
                code=400
            )
        
        # 성향분석 수행 (user_id가 None이면 익명 사용자)
        result = analysis_service.analyze_personality(answers, analysis_type_id, user_id)
        
        # SQLAlchemy 모델을 Pydantic 스키마로 변환
        response_data = AnalysisResultResponse(
            id=result.id,
            user_id=result.user_id,
            analysis_type_id=result.analysis_type_id,
            empathy_score=result.empathy_score,
            active_score=result.active_score,
            plan_score=result.plan_score,
            express_score=result.express_score,
            personality_type=result.personality_type,
            description=result.description,
            recommendations=result.recommendations,
            created_at=result.created_at
        )
        
        message = "성향분석이 완료되었습니다."
        if user_id is None:
            message += " (익명 사용자)"
        
        return SuccessResponse(
            data=response_data,
            message=message,
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"성향분석 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.get("/results/{result_id}", response_model=ApiResponse)
async def get_analysis_result(result_id: str):
    """특정 성향분석 결과를 조회합니다. (익명 사용자 결과도 조회 가능)"""
    try:
        result = analysis_service.get_analysis_result(result_id)
        if not result:
            return ErrorResponse(
                message="분석 결과를 찾을 수 없습니다.",
                code=404
            )
        
        # SQLAlchemy 모델을 Pydantic 스키마로 변환
        response_data = AnalysisResultResponse(
            id=result.id,
            user_id=result.user_id,
            analysis_type_id=result.analysis_type_id,
            empathy_score=result.empathy_score,
            active_score=result.active_score,
            plan_score=result.plan_score,
            express_score=result.express_score,
            personality_type=result.personality_type,
            description=result.description,
            recommendations=result.recommendations,
            created_at=result.created_at
        )
        
        # 익명 사용자 여부 확인
        is_anonymous = result.user_id is None
        message = "분석 결과를 성공적으로 조회했습니다."
        if is_anonymous:
            message += " (익명 사용자 결과)"
        
        return SuccessResponse(
            data=response_data,
            message=message,
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"분석 결과 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.get("/anonymous/results/{result_id}", response_model=ApiResponse)
async def get_anonymous_result(result_id: str):
    """익명 사용자의 성향분석 결과를 조회합니다."""
    try:
        result = analysis_service.get_analysis_result(result_id)
        if not result:
            return ErrorResponse(
                message="분석 결과를 찾을 수 없습니다.",
                code=404
            )
        
        # 익명 사용자 결과인지 확인
        if result.user_id is not None:
            return ErrorResponse(
                message="이 결과는 익명 사용자 결과가 아닙니다.",
                code=403
            )
        
        return SuccessResponse(
            data=result,
            message="익명 사용자 분석 결과를 성공적으로 조회했습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"익명 사용자 결과 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )
