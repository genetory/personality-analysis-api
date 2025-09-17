from app.models.analysis import Analysis
from app.models.question import Question
from app.models.question_option import QuestionOption

# 모델들 간의 관계 설정
from sqlalchemy.orm import configure_mappers

# 관계 매핑 구성
configure_mappers()

__all__ = [
    "Analysis",
    "Question",
    "QuestionOption"
]