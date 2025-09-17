from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "성향분석 API"
    
    # CORS 설정
    ALLOWED_HOSTS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    # MySQL 데이터베이스 설정
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "genetory"
    MYSQL_PASSWORD: str = "?Shjy20733"
    MYSQL_DATABASE: str = "personality-analysis"
    
    # JWT 설정 (향후 사용자 인증용)
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis 설정 (향후 캐싱용)
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI 설정
    OPENAI_API_KEY: str = ""  # 환경변수에서 로드
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()