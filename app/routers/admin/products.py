from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from typing import Optional

from app.database import get_session
from app.dependencies import get_templates, get_current_admin_user
from app.crud import product as product_crud, category as category_crud
from app.models import ProductCreate, ProductUpdate

router = APIRouter(prefix="/admin/products", tags=["admin-products"])


@router.get("")
async def product_list(
    request: Request,
    category_id: int | None = None,
    page: int = 1,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """상품 목록"""
    per_page = 20
    skip = (page - 1) * per_page

    products = product_crud.get_products(
        session,
        category_id=category_id,
        active_only=False,
        skip=skip,
        limit=per_page
    )
    total = product_crud.count_products(session, category_id=category_id, active_only=False)
    categories = category_crud.get_categories(session, active_only=False)

    return templates.TemplateResponse(
        "admin/products/list.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "selected_category": category_id,
            "page": page,
            "total": total,
            "per_page": per_page
        }
    )


@router.get("/new")
async def product_new(
    request: Request,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """상품 등록 폼"""
    categories = category_crud.get_categories(session)
    return templates.TemplateResponse(
        "admin/products/form.html",
        {"request": request, "product": None, "categories": categories, "errors": {}}
    )


@router.post("/new")
async def product_create(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    price: int = Form(...),
    original_price: int = Form(None),
    stock: int = Form(0),
    category_id: int = Form(...),
    is_active: bool = Form(False),
    is_featured: bool = Form(False),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """상품 등록"""
    existing = product_crud.get_product_by_slug(session, slug)
    if existing:
        categories = category_crud.get_categories(session)
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "product": None,
                "categories": categories,
                "errors": {"slug": "이미 사용 중인 슬러그입니다"}
            }
        )

    product_data = ProductCreate(
        name=name,
        slug=slug,
        description=description,
        price=price,
        original_price=original_price,
        stock=stock,
        category_id=category_id,
        is_active=is_active,
        is_featured=is_featured
    )
    product_crud.create_product(session, product_data)

    return RedirectResponse(url="/admin/products", status_code=303)


@router.get("/{product_id}/edit")
async def product_edit(
    request: Request,
    product_id: int,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """상품 수정 폼"""
    product = product_crud.get_product(session, product_id)
    if not product:
        return RedirectResponse(url="/admin/products", status_code=303)

    categories = category_crud.get_categories(session)
    return templates.TemplateResponse(
        "admin/products/form.html",
        {"request": request, "product": product, "categories": categories, "errors": {}}
    )


@router.post("/{product_id}/edit")
async def product_update(
    request: Request,
    product_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    price: int = Form(...),
    original_price: int = Form(None),
    stock: int = Form(0),
    category_id: int = Form(...),
    is_active: bool = Form(False),
    is_featured: bool = Form(False),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """상품 수정"""
    product = product_crud.get_product(session, product_id)
    if not product:
        return RedirectResponse(url="/admin/products", status_code=303)

    prod_update = ProductUpdate(
        name=name,
        slug=slug,
        description=description,
        price=price,
        original_price=original_price,
        stock=stock,
        category_id=category_id,
        is_active=is_active,
        is_featured=is_featured
    )
    product_crud.update_product(session, product, prod_update)

    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/{product_id}/delete")
async def product_delete(
    product_id: int,
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """상품 삭제"""
    product = product_crud.get_product(session, product_id)
    if product:
        product_crud.delete_product(session, product)
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/{product_id}/images")
async def upload_product_image(
    request: Request,
    product_id: int,
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """상품 이미지 업로드"""
    from app.services.image import save_image
    from app.models import ProductImage

    product = product_crud.get_product(session, product_id)
    if not product:
        raise HTTPException(404, "상품을 찾을 수 없습니다")

    # 이미지 저장
    url = await save_image(image, folder="products")

    # DB에 저장
    product_image = ProductImage(
        product_id=product_id,
        url=url,
        sort_order=len(product.images)
    )
    session.add(product_image)
    session.commit()

    return RedirectResponse(url=f"/admin/products/{product_id}/edit", status_code=303)


@router.post("/{product_id}/images/{image_id}/delete")
async def delete_product_image(
    product_id: int,
    image_id: int,
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """상품 이미지 삭제"""
    from app.services.image import delete_image
    from app.models import ProductImage

    image = session.get(ProductImage, image_id)
    if image and image.product_id == product_id:
        delete_image(image.url)
        session.delete(image)
        session.commit()

    return RedirectResponse(url=f"/admin/products/{product_id}/edit", status_code=303)
