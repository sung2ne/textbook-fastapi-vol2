from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user, get_current_cart
from app.crud import cart as cart_crud, user as user_crud
from app.models import User, Cart
from app.services.cart_validation import validate_cart, CartValidationError
from app.services.shipping import calculate_shipping_fee

router = APIRouter(tags=["checkout"])


@router.get("/checkout")
async def checkout_page(
    request: Request,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user),
    cart: Cart | None = Depends(get_current_cart)
):
    """주문서 작성 페이지"""
    # 장바구니 확인
    if not cart or not cart.items:
        return RedirectResponse(url="/cart", status_code=303)

    # 장바구니 검증
    try:
        validate_cart(session, cart)
    except CartValidationError as e:
        return templates.TemplateResponse(
            "checkout/error.html",
            {"request": request, "errors": e.errors}
        )

    # 배송지 목록
    addresses = user_crud.get_user_addresses(session, user.id)
    default_address = next((a for a in addresses if a.is_default), None)

    # 배송비 계산
    shipping_fee = calculate_shipping_fee(cart.total_price)
    final_price = cart.total_price + shipping_fee

    return templates.TemplateResponse(
        "checkout/index.html",
        {
            "request": request,
            "cart": cart,
            "addresses": addresses,
            "default_address": default_address,
            "shipping_fee": shipping_fee,
            "final_price": final_price
        }
    )
