from typing import Any, Optional
from pydantic import BaseModel

class ApiResponse(BaseModel):
    """표준 API 응답 모델"""
    data: Optional[Any] = None
    message: str
    code: int

class SuccessResponse(ApiResponse):
    """성공 응답"""
    def __init__(self, data: Any = None, message: str = "성공", code: int = 200):
        super().__init__(data=data, message=message, code=code)

class ErrorResponse(ApiResponse):
    """에러 응답"""
    def __init__(self, message: str = "오류가 발생했습니다", code: int = 500, data: Any = None):
        super().__init__(data=data, message=message, code=code)
