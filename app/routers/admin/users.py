from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_admin_user
from app.crud import user as user_crud, order as order_crud
from app.models import User, UserRole

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.get("")
async def user_list(
    request: Request,
    search: str | None = None,
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """회원 목록"""
    per_page = 20
    skip = (page - 1) * per_page

    users = user_crud.get_all_users(session, search=search, skip=skip, limit=per_page)
    total = user_crud.count_users(session, search=search)

    return templates.TemplateResponse(
        "admin/users/list.html",
        {
            "request": request,
            "users": users,
            "search": search,
            "page": page,
            "total": total,
            "per_page": per_page
        }
    )


@router.get("/{user_id}")
async def user_detail(
    request: Request,
    user_id: int,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """회원 상세"""
    user = user_crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")

    # 회원 주문 내역
    orders = order_crud.get_user_orders(session, user_id, limit=10)

    return templates.TemplateResponse(
        "admin/users/detail.html",
        {
            "request": request,
            "user": user,
            "orders": orders
        }
    )


@router.post("/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool = Form(...),
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """회원 상태 변경"""
    user = user_crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")

    # 자기 자신은 비활성화 불가
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="자기 자신은 비활성화할 수 없습니다")

    user_crud.update_user_status(session, user, is_active)

    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.post("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str = Form(...),
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """회원 역할 변경"""
    user = user_crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")

    # 자기 자신의 역할은 변경 불가
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="자기 자신의 역할은 변경할 수 없습니다")

    try:
        new_role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 역할입니다")

    user_crud.update_user_role(session, user, new_role)

    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)
