from contextlib import asynccontextmanager
from datetime import datetime
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

# 업로드 폴더 서빙
import os
upload_dir = settings.UPLOAD_DIR
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# 템플릿
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# 커스텀 필터 등록
def format_price(value: int) -> str:
    """가격 포맷 (1000 -> 1,000)"""
    return f"{value:,}"


def format_datetime_filter(value: datetime, format: str = "%Y-%m-%d %H:%M") -> str:
    """날짜 포맷"""
    if value is None:
        return ""
    return value.strftime(format)


def format_date(value: datetime) -> str:
    """날짜만"""
    return format_datetime_filter(value, "%Y-%m-%d")


def nl2br(value: str) -> str:
    """줄바꿈을 <br>로 변환"""
    from markupsafe import Markup
    return Markup(value.replace("\n", "<br>"))


def format_phone(value: str) -> str:
    """전화번호 포맷"""
    if len(value) == 11:
        return f"{value[:3]}-{value[3:7]}-{value[7:]}"
    return value


def status_text(status) -> str:
    """주문 상태 한글"""
    texts = {
        "pending": "결제 대기",
        "paid": "결제 완료",
        "preparing": "배송 준비",
        "shipping": "배송 중",
        "delivered": "배송 완료",
        "cancelled": "취소됨"
    }
    val = status.value if hasattr(status, 'value') else status
    return texts.get(val, val)


def status_badge(status) -> str:
    """주문 상태 뱃지 클래스"""
    badges = {
        "pending": "bg-warning text-dark",
        "paid": "bg-success",
        "preparing": "bg-info",
        "shipping": "bg-primary",
        "delivered": "bg-secondary",
        "cancelled": "bg-danger"
    }
    val = status.value if hasattr(status, 'value') else status
    return badges.get(val, "bg-secondary")


templates.env.filters["format_price"] = format_price
templates.env.filters["format_datetime"] = format_datetime_filter
templates.env.filters["format_date"] = format_date
templates.env.filters["nl2br"] = nl2br
templates.env.filters["format_phone"] = format_phone
templates.env.filters["status_text"] = status_text
templates.env.filters["status_badge"] = status_badge

# 전역 변수
templates.env.globals["site_name"] = settings.SITE_NAME
templates.env.globals["current_user"] = None
templates.env.globals["cart_count"] = 0

# 라우터 등록
from app.routers import products, auth, mypage, checkout, orders
from app.routers.cart import router as cart_api_router, page_router as cart_page_router
from app.routers.admin import categories as admin_categories, products as admin_products

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(mypage.router)
app.include_router(cart_api_router)
app.include_router(cart_page_router)
app.include_router(checkout.router)
app.include_router(orders.router)
app.include_router(admin_categories.router)
app.include_router(admin_products.router)


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
