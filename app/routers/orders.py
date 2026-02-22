from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user
from app.crud import order as order_crud
from app.models import User, OrderStatus, PaymentStatus
from app.services.order_validation import (
    validate_order_access,
    validate_order_cancellable,
    OrderAccessError
)
from app.services.toss import cancel_payment

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
async def order_list(
    request: Request,
    page: int = 1,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """주문 내역 목록"""
    per_page = 10
    skip = (page - 1) * per_page

    orders = order_crud.get_user_orders(session, user.id, skip=skip, limit=per_page)

    return templates.TemplateResponse(
        "orders/list.html",
        {
            "request": request,
            "orders": orders,
            "page": page
        }
    )


@router.get("/{order_number}")
async def order_detail(
    request: Request,
    order_number: str,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """주문 상세"""
    order = order_crud.get_order_by_number(session, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    try:
        validate_order_access(session, order, user)
    except OrderAccessError:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    return templates.TemplateResponse(
        "orders/detail.html",
        {"request": request, "order": order}
    )


@router.post("/{order_number}/cancel")
async def cancel_order(
    order_number: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """주문 취소"""
    order = order_crud.get_order_by_number(session, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    try:
        validate_order_access(session, order, user)
        validate_order_cancellable(order)
    except OrderAccessError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 결제 완료된 경우 PG사 취소
    if order.status == OrderStatus.PAID and order.payment and order.payment.payment_key:
        result = await cancel_payment(
            order.payment.payment_key,
            "고객 요청에 의한 취소"
        )

        if not result["success"]:
            error = result["error"]
            raise HTTPException(
                status_code=400,
                detail=f"결제 취소 실패: {error.get('message')}"
            )

        # 결제 상태 업데이트
        order.payment.status = PaymentStatus.CANCELLED
        session.add(order.payment)

    # 주문 취소
    order_crud.cancel_order(session, order)

    return RedirectResponse(url=f"/orders/{order_number}", status_code=303)
