from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from pathlib import Path
from datetime import datetime

from app.database import get_session

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# 커스텀 필터 등록
def format_price(value: int) -> str:
    return f"{value:,}"


def format_datetime_filter(value: datetime, format: str = "%Y-%m-%d %H:%M") -> str:
    if value is None:
        return ""
    return value.strftime(format)


def format_date(value: datetime) -> str:
    return format_datetime_filter(value, "%Y-%m-%d")


def status_text(status) -> str:
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
templates.env.filters["status_text"] = status_text
templates.env.filters["status_badge"] = status_badge
templates.env.globals["site_name"] = "FastAPI Shop"


def flash(request: Request, message: str, category: str = "info"):
    """플래시 메시지 추가"""
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


async def get_templates():
    """템플릿 인스턴스 반환"""
    return templates


async def get_current_user_optional(
    request: Request,
    session: Session = Depends(get_session)
):
    """현재 사용자 (로그인 선택)"""
    from app.services.session import get_session as get_user_session
    from app.crud import user as user_crud

    user_session = get_user_session(request)
    if not user_session:
        templates.env.globals["current_user"] = None
        templates.env.globals["cart_count"] = 0
        return None

    user_id = user_session.get("user_id")
    if not user_id:
        templates.env.globals["current_user"] = None
        return None

    user = user_crud.get_user(session, user_id)
    templates.env.globals["current_user"] = user
    return user


async def get_current_user(
    user=Depends(get_current_user_optional)
):
    """현재 사용자 (로그인 필수)"""
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    return user


async def get_current_admin_user(
    user=Depends(get_current_user)
):
    """관리자 사용자"""
    from app.models import UserRole
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    return user


async def require_login(request: Request, user=Depends(get_current_user_optional)):
    """로그인 필수 (리다이렉트)"""
    if not user:
        return RedirectResponse(
            url=f"/login?next={request.url.path}",
            status_code=303
        )
    return user
