from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from pathlib import Path

from app.database import get_session

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def flash(request: Request, message: str, category: str = "info"):
    """플래시 메시지 추가"""
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request) -> list:
    """플래시 메시지 가져오기 (한 번만)"""
    messages = request.session.pop("_messages", [])
    return messages


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
        return None

    user_id = user_session.get("user_id")
    if not user_id:
        return None

    return user_crud.get_user(session, user_id)


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
    from fastapi.responses import RedirectResponse
    if not user:
        return RedirectResponse(
            url=f"/login?next={request.url.path}",
            status_code=303
        )
    return user
