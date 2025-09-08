from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.response import ApiResponse, SuccessResponse, ErrorResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_results(user_id: int):
    """특정 사용자의 모든 성향분석 결과를 조회합니다."""
    try:
        # TODO: 실제 사용자 결과 조회 로직 구현
        results = []
        
        return SuccessResponse(
            data=results,
            message="사용자의 성향분석 결과를 성공적으로 조회했습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"사용자 결과 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.get("/anonymous", response_model=ApiResponse)
async def get_anonymous_results():
    """익명 사용자들의 성향분석 결과 통계를 조회합니다."""
    try:
        stats = analysis_service.get_anonymous_results_stats()
        
        return SuccessResponse(
            data=stats,
            message="익명 사용자 결과 통계를 성공적으로 조회했습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"익명 사용자 통계 조회 중 오류가 발생했습니다: {str(e)}",
            code=500
        )

@router.delete("/{result_id}", response_model=ApiResponse)
async def delete_result(result_id: str):
    """특정 성향분석 결과를 삭제합니다."""
    try:
        # TODO: 실제 결과 삭제 로직 구현
        
        return SuccessResponse(
            data=None,
            message="성향분석 결과가 성공적으로 삭제되었습니다.",
            code=200
        )
    except Exception as e:
        return ErrorResponse(
            message=f"결과 삭제 중 오류가 발생했습니다: {str(e)}",
            code=500
        )
