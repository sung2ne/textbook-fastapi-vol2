from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user_optional
from app.models import UserLogin, UserRole
from app.services.auth import authenticate_user, AuthError
from app.services.session import create_session

router = APIRouter(prefix="/admin", tags=["admin-auth"])


@router.get("/login")
async def admin_login_form(
    request: Request,
    templates=Depends(get_templates),
    user=Depends(get_current_user_optional)
):
    """관리자 로그인 폼"""
    if user and user.role == UserRole.ADMIN:
        return RedirectResponse(url="/admin", status_code=303)

    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "errors": {}}
    )


@router.post("/login")
async def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
    templates=Depends(get_templates)
):
    """관리자 로그인 처리"""
    try:
        user_login = UserLogin(email=email, password=password)
        user = authenticate_user(session, user_login)

        # 관리자 권한 확인
        if user.role != UserRole.ADMIN:
            raise AuthError("관리자 권한이 없습니다")

        response = RedirectResponse(url="/admin", status_code=303)
        create_session(response, user.id)
        return response

    except AuthError as e:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "errors": {"general": str(e)},
                "email": email
            }
        )
