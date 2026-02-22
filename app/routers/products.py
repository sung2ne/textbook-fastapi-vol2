from fastapi import APIRouter, Depends, Request, Query
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates
from app.crud import product as product_crud, category as category_crud

router = APIRouter(tags=["products"])


@router.get("/products")
async def product_list(
    request: Request,
    category: str | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
    templates=Depends(get_templates)
):
    """상품 목록"""
    per_page = 12
    skip = (page - 1) * per_page

    # 카테고리 필터
    category_id = None
    selected_category = None
    if category:
        selected_category = category_crud.get_category_by_slug(session, category)
        if selected_category:
            category_id = selected_category.id

    # 검색 또는 목록
    if q:
        products = product_crud.search_products(session, q, skip=skip, limit=per_page)
        total = len(product_crud.search_products(session, q))
    else:
        products = product_crud.get_products(
            session,
            category_id=category_id,
            skip=skip,
            limit=per_page
        )
        total = product_crud.count_products(session, category_id=category_id)

    categories = category_crud.get_categories(session)
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        "products/list.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "query": q,
            "page": page,
            "total_pages": total_pages,
            "total": total
        }
    )


@router.get("/products/{slug}")
async def product_detail(
    request: Request,
    slug: str,
    session: Session = Depends(get_session),
    templates=Depends(get_templates)
):
    """상품 상세"""
    product = product_crud.get_product_by_slug(session, slug)
    if not product or not product.is_active:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404
        )

    # 관련 상품 (같은 카테고리)
    related_products = []
    if product.category_id:
        related_products = product_crud.get_products(
            session,
            category_id=product.category_id,
            limit=4
        )
        related_products = [p for p in related_products if p.id != product.id][:4]

    return templates.TemplateResponse(
        "products/detail.html",
        {
            "request": request,
            "product": product,
            "related_products": related_products
        }
    )
