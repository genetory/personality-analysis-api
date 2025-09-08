from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analysis, users, results
from app.core.config import settings
from app.schemas.response import ApiResponse, SuccessResponse

app = FastAPI(
    title="성향분석 API",
    description="4축 성향분석 플랫폼을 위한 REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(results.router, prefix="/api/v1/results", tags=["results"])

@app.get("/", response_model=ApiResponse)
async def root():
    return SuccessResponse(
        data={"message": "성향분석 API 서버가 실행 중입니다."},
        message="API 서버가 정상적으로 실행 중입니다.",
        code=200
    )

@app.get("/health", response_model=ApiResponse)
async def health_check():
    return SuccessResponse(
        data={"status": "healthy"},
        message="서버 상태가 정상입니다.",
        code=200
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
