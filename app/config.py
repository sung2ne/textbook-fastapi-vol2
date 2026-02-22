from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 데이터베이스
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 앱 설정
    DEBUG: bool = False
    SITE_NAME: str = "FastAPI Shop"

    # 파일 업로드
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # 결제
    TOSS_CLIENT_KEY: str = ""
    TOSS_SECRET_KEY: str = ""

    # URL
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
