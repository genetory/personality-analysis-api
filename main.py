from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import analysis_router, responses_router, results_router, comments_router, result_types
from app.api.ai_analysis import router as ai_analysis_router

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
    responses_router,
    prefix=f"{settings.API_V1_STR}/responses",
    tags=["responses"]
)

app.include_router(
    results_router,
    prefix=f"{settings.API_V1_STR}/results",
    tags=["results"]
)

app.include_router(
    comments_router,
    prefix=f"{settings.API_V1_STR}/comments",
    tags=["comments"]
)

app.include_router(
    result_types.router,
    prefix=f"{settings.API_V1_STR}/result-types",
    tags=["result-types"]
)

app.include_router(
    ai_analysis_router,
    prefix=f"{settings.API_V1_STR}/ai-analysis",
    tags=["ai-analysis"]
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
