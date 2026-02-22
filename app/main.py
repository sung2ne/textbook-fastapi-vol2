from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings

# 경로 설정
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    print(f"{settings.SITE_NAME} 시작")
    yield
    print(f"{settings.SITE_NAME} 종료")


app = FastAPI(
    title=settings.SITE_NAME,
    description="FastAPI로 만든 쇼핑몰",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 템플릿
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
async def home(request: Request):
    """홈 페이지"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "site_name": settings.SITE_NAME}
    )


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "ok"}
