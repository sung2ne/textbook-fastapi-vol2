from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user
from app.models import User
from app.crud import user as user_crud

router = APIRouter(prefix="/mypage", tags=["mypage"])


@router.get("")
async def mypage(
    request: Request,
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """마이페이지"""
    return templates.TemplateResponse(
        "mypage/index.html",
        {"request": request, "user": user}
    )


@router.get("/edit")
async def edit_profile_form(
    request: Request,
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """회원정보 수정 폼"""
    return templates.TemplateResponse(
        "mypage/edit.html",
        {"request": request, "user": user, "errors": {}}
    )


@router.post("/edit")
async def edit_profile(
    request: Request,
    name: str = Form(...),
    phone: str = Form(""),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """회원정보 수정"""
    user.name = name
    user.phone = phone if phone else None
    session.add(user)
    session.commit()

    return RedirectResponse(url="/mypage", status_code=303)


@router.get("/password")
async def change_password_form(
    request: Request,
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """비밀번호 변경 폼"""
    return templates.TemplateResponse(
        "mypage/password.html",
        {"request": request, "errors": {}}
    )


@router.post("/password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """비밀번호 변경"""
    from app.services.password import verify_password, hash_password, validate_password, PasswordError

    errors = {}

    if not verify_password(current_password, user.hashed_password):
        errors["current_password"] = "현재 비밀번호가 올바르지 않습니다"

    if new_password != new_password_confirm:
        errors["new_password_confirm"] = "새 비밀번호가 일치하지 않습니다"

    if not errors:
        try:
            validate_password(new_password)
        except PasswordError as e:
            errors["new_password"] = str(e)

    if errors:
        return templates.TemplateResponse(
            "mypage/password.html",
            {"request": request, "errors": errors}
        )

    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()

    return RedirectResponse(url="/mypage", status_code=303)
