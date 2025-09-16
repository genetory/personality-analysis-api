"""
UUID 유틸리티 함수들
"""

import uuid
from typing import Optional


def generate_uuid() -> str:
    """UUID4를 문자열로 생성"""
    return str(uuid.uuid4())


def is_valid_uuid(uuid_string: str) -> bool:
    """UUID 문자열이 유효한지 검증"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def format_uuid(uuid_string: str) -> Optional[str]:
    """UUID 문자열을 표준 형식으로 포맷팅"""
    try:
        return str(uuid.UUID(uuid_string))
    except ValueError:
        return None
