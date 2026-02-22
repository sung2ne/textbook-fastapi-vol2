from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_admin_user
from app.crud import category as category_crud
from app.models import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/admin/categories", tags=["admin-categories"])


@router.get("")
async def category_list(
    request: Request,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """카테고리 목록"""
    categories = category_crud.get_categories(session, active_only=False)
    return templates.TemplateResponse(
        "admin/categories/list.html",
        {"request": request, "categories": categories}
    )


@router.get("/new")
async def category_new(
    request: Request,
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """카테고리 등록 폼"""
    return templates.TemplateResponse(
        "admin/categories/form.html",
        {"request": request, "category": None, "errors": {}}
    )


@router.post("/new")
async def category_create(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    sort_order: int = Form(0),
    is_active: bool = Form(False),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """카테고리 등록"""
    existing = category_crud.get_category_by_slug(session, slug)
    if existing:
        return templates.TemplateResponse(
            "admin/categories/form.html",
            {
                "request": request,
                "category": None,
                "errors": {"slug": "이미 사용 중인 슬러그입니다"}
            }
        )

    category_create = CategoryCreate(
        name=name,
        slug=slug,
        description=description,
        sort_order=sort_order,
        is_active=is_active
    )
    category_crud.create_category(session, category_create)

    return RedirectResponse(url="/admin/categories", status_code=303)


@router.get("/{category_id}/edit")
async def category_edit(
    request: Request,
    category_id: int,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """카테고리 수정 폼"""
    category = category_crud.get_category(session, category_id)
    if not category:
        return RedirectResponse(url="/admin/categories", status_code=303)

    return templates.TemplateResponse(
        "admin/categories/form.html",
        {"request": request, "category": category, "errors": {}}
    )


@router.post("/{category_id}/edit")
async def category_update(
    request: Request,
    category_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    sort_order: int = Form(0),
    is_active: bool = Form(False),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """카테고리 수정"""
    category = category_crud.get_category(session, category_id)
    if not category:
        return RedirectResponse(url="/admin/categories", status_code=303)

    cat_update = CategoryUpdate(
        name=name,
        slug=slug,
        description=description,
        sort_order=sort_order,
        is_active=is_active
    )
    category_crud.update_category(session, category, cat_update)

    return RedirectResponse(url="/admin/categories", status_code=303)


@router.post("/{category_id}/delete")
async def category_delete(
    category_id: int,
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """카테고리 삭제"""
    category = category_crud.get_category(session, category_id)
    if category:
        category_crud.delete_category(session, category)
    return RedirectResponse(url="/admin/categories", status_code=303)
