from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user, get_current_cart
from app.crud import cart as cart_crud, user as user_crud, order as order_crud
from app.models import User, Cart, AddressCreate
from app.services.cart_validation import validate_cart, CartValidationError
from app.services.shipping import calculate_shipping_fee
from app.services.order_number import generate_order_number

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


@router.post("/checkout")
async def create_order(
    request: Request,
    recipient: str = Form(...),
    phone: str = Form(...),
    zipcode: str = Form(...),
    address1: str = Form(...),
    address2: str = Form(None),
    memo: str = Form(None),
    save_address: bool = Form(False),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user),
    cart: Cart | None = Depends(get_current_cart)
):
    """주문 생성"""
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

    # 배송비 계산
    shipping_fee = calculate_shipping_fee(cart.total_price)

    # 주문 생성
    order_number = generate_order_number()
    order = order_crud.create_order(
        session=session,
        user_id=user.id,
        order_number=order_number,
        total_price=cart.total_price,
        shipping_fee=shipping_fee,
        recipient=recipient,
        phone=phone,
        zipcode=zipcode,
        address1=address1,
        address2=address2,
        memo=memo,
        cart_items=cart.items
    )

    # 재고 차감
    for item in cart.items:
        item.product.stock -= item.quantity
        session.add(item.product)

    # 장바구니 비우기
    cart_crud.clear_cart(session, cart)

    # 배송지 저장
    if save_address:
        address_create = AddressCreate(
            name="새 배송지",
            recipient=recipient,
            phone=phone,
            zipcode=zipcode,
            address1=address1,
            address2=address2,
            is_default=False
        )
        user_crud.create_address(session, user.id, address_create)

    session.commit()

    # 결제 페이지로 이동
    return RedirectResponse(
        url=f"/payment/{order.order_number}",
        status_code=303
    )
