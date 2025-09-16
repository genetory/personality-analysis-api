from app.api.analysis import router as analysis_router
from app.api.responses import router as responses_router
from app.api.results import router as results_router
from app.api.comments import router as comments_router

__all__ = [
    "analysis_router",
    "responses_router",
    "results_router",
    "comments_router"
]