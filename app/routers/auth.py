from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user_optional
from app.models import UserCreate, UserLogin
from app.services.auth import register_user, authenticate_user, AuthError
from app.services.session import create_session, destroy_session
from app.services.cart_session import get_cart_session_id, clear_cart_session_cookie

router = APIRouter(tags=["auth"])


@router.get("/register")
async def register_form(
    request: Request,
    templates=Depends(get_templates),
    user=Depends(get_current_user_optional)
):
    """회원가입 폼"""
    if user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "errors": {}}
    )


@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    name: str = Form(...),
    phone: str = Form(""),
    session: Session = Depends(get_session),
    templates=Depends(get_templates)
):
    """회원가입 처리"""
    errors = {}

    if password != password_confirm:
        errors["password_confirm"] = "비밀번호가 일치하지 않습니다"

    if errors:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": errors,
                "email": email,
                "name": name,
                "phone": phone
            }
        )

    try:
        user_create = UserCreate(
            email=email,
            password=password,
            name=name,
            phone=phone if phone else None
        )
        register_user(session, user_create)

        return RedirectResponse(
            url="/login?message=registered",
            status_code=303
        )

    except AuthError as e:
        errors["general"] = str(e)
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "errors": errors,
                "email": email,
                "name": name,
                "phone": phone
            }
        )


@router.get("/login")
async def login_form(
    request: Request,
    message: str | None = None,
    next: str | None = None,
    templates=Depends(get_templates),
    user=Depends(get_current_user_optional)
):
    """로그인 폼"""
    if user:
        return RedirectResponse(url="/", status_code=303)

    messages = {
        "registered": "회원가입이 완료되었습니다. 로그인해주세요.",
        "logout": "로그아웃되었습니다."
    }

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "message": messages.get(message),
            "next": next,
            "errors": {}
        }
    )


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    session: Session = Depends(get_session),
    templates=Depends(get_templates)
):
    """로그인 처리"""
    try:
        user_login = UserLogin(email=email, password=password)
        user = authenticate_user(session, user_login)

        response = RedirectResponse(url=next, status_code=303)
        create_session(response, user.id)

        # 비회원 장바구니 병합
        from app.crud import cart as cart_crud
        guest_session_id = get_cart_session_id(request)
        if guest_session_id:
            try:
                guest_cart = cart_crud.get_or_create_cart(
                    session,
                    session_id=guest_session_id
                )
                if guest_cart.items:
                    user_cart = cart_crud.get_or_create_cart(
                        session,
                        user_id=user.id
                    )
                    cart_crud.merge_carts(session, user_cart, guest_cart)
                clear_cart_session_cookie(response)
            except Exception:
                pass

        return response

    except AuthError as e:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "errors": {"general": str(e)},
                "email": email,
                "next": next
            }
        )


@router.post("/logout")
async def logout(request: Request):
    """로그아웃"""
    response = RedirectResponse(url="/login?message=logout", status_code=303)
    destroy_session(response)
    return response
