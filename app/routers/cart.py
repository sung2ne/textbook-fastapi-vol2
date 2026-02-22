import uuid
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user_optional, get_current_cart
from app.crud import cart as cart_crud, product as product_crud
from app.models import Cart, User
from app.schemas.cart import AddToCartRequest, UpdateCartItemRequest

# API 라우터
router = APIRouter(prefix="/api/cart", tags=["cart-api"])

# 페이지 라우터
page_router = APIRouter(tags=["cart-page"])


def get_cart_identifier(request: Request, user: User | None):
    """장바구니 식별자 반환"""
    if user:
        return {"user_id": user.id}
    else:
        session_id = request.cookies.get("cart_session")
        if not session_id:
            session_id = str(uuid.uuid4())
        return {"session_id": session_id}


@router.post("/add")
async def add_to_cart(
    request: Request,
    data: AddToCartRequest,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user_optional)
):
    """장바구니 담기"""
    # 상품 확인
    product = product_crud.get_product(session, data.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # 재고 확인
    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="재고가 부족합니다")

    # 장바구니 가져오기
    identifier = get_cart_identifier(request, user)
    cart = cart_crud.get_or_create_cart(session, **identifier)

    # 상품 추가
    item = cart_crud.add_to_cart(session, cart, data.product_id, data.quantity)

    # 응답
    response = JSONResponse({
        "success": True,
        "message": "장바구니에 담았습니다",
        "cart_quantity": cart.total_quantity
    })

    # 비회원인 경우 세션 쿠키 설정
    if not user and "session_id" in identifier:
        response.set_cookie(
            key="cart_session",
            value=identifier["session_id"],
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=True
        )

    return response


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    data: UpdateCartItemRequest,
    session: Session = Depends(get_session)
):
    """수량 변경"""
    item = cart_crud.update_cart_item(session, item_id, data.quantity)

    if data.quantity <= 0:
        return {"success": True, "message": "상품이 삭제되었습니다"}

    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    return {
        "success": True,
        "quantity": item.quantity,
        "subtotal": item.subtotal
    }


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    """상품 삭제"""
    success = cart_crud.remove_from_cart(session, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    return {"success": True, "message": "삭제되었습니다"}


# 페이지 라우터
@page_router.get("/cart")
async def cart_page(
    request: Request,
    templates=Depends(get_templates),
    cart: Cart | None = Depends(get_current_cart)
):
    """장바구니 페이지"""
    return templates.TemplateResponse(
        "cart/index.html",
        {
            "request": request,
            "cart": cart
        }
    )


@page_router.post("/cart/update/{item_id}")
async def update_item_form(
    item_id: int,
    quantity: int = Form(...),
    session: Session = Depends(get_session)
):
    """수량 변경 (폼)"""
    cart_crud.update_cart_item(session, item_id, quantity)
    return RedirectResponse(url="/cart", status_code=303)


@page_router.post("/cart/remove/{item_id}")
async def remove_item_form(
    item_id: int,
    session: Session = Depends(get_session)
):
    """상품 삭제 (폼)"""
    cart_crud.remove_from_cart(session, item_id)
    return RedirectResponse(url="/cart", status_code=303)


@page_router.post("/cart/clear")
async def clear_cart_form(
    session: Session = Depends(get_session),
    cart: Cart | None = Depends(get_current_cart)
):
    """장바구니 비우기"""
    if cart:
        cart_crud.clear_cart(session, cart)
    return RedirectResponse(url="/cart", status_code=303)
