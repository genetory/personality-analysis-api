from app.models.analysis import Analysis
from app.models.dimension import Dimension
from app.models.question import Question
from app.models.option import Option
from app.models.option_score import OptionScore
from app.models.response import Response
from app.models.result import Result
from app.models.comment import Comment
from app.models.result_type import ResultType
from app.models.result_interpretation import ResultInterpretation

# 모델들 간의 관계 설정
from sqlalchemy.orm import configure_mappers

# 관계 설정을 위한 import
from app.models.analysis import Analysis
from app.models.dimension import Dimension
from app.models.question import Question
from app.models.option import Option
from app.models.option_score import OptionScore
from app.models.response import Response
from app.models.result import Result
from app.models.comment import Comment
from app.models.result_type import ResultType
from app.models.result_interpretation import ResultInterpretation

# 관계 매핑 구성
configure_mappers()

__all__ = [
    "Analysis",
    "Dimension", 
    "Question",
    "Option",
    "OptionScore",
    "Response",
    "Result",
    "Comment",
    "ResultType",
    "ResultInterpretation"
]