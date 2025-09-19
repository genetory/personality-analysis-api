from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import analysis_router
from app.api.personality_results import router as personality_results_router
from app.api.analysis_results import router as analysis_results_router
from app.api.comments import router as comments_router

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="성향분석 서비스를 위한 REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(
    analysis_router,
    prefix=f"{settings.API_V1_STR}/analysis",
    tags=["analysis"]
)

app.include_router(
    personality_results_router,
    prefix=f"{settings.API_V1_STR}",
    tags=["personality-results"]
)

app.include_router(
    analysis_results_router,
    prefix=f"{settings.API_V1_STR}",
    tags=["analysis-results"]
)

app.include_router(
    comments_router,
    prefix=f"{settings.API_V1_STR}",
    tags=["comments"]
)




@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "성향분석 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
