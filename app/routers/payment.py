from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_user
from app.crud import order as order_crud
from app.models import User, OrderStatus, PaymentStatus
from app.services.order_validation import validate_order_access, OrderAccessError
from app.services.toss import confirm_payment
from app.config import settings

router = APIRouter(prefix="/payment", tags=["payment"])


@router.get("/{order_number}")
async def payment_page(
    request: Request,
    order_number: str,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """결제 페이지"""
    order = order_crud.get_order_by_number(session, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    try:
        validate_order_access(session, order, user)
    except OrderAccessError:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 이미 결제된 주문
    if order.status != OrderStatus.PENDING:
        return RedirectResponse(url=f"/orders/{order_number}", status_code=303)

    return templates.TemplateResponse(
        "payment/checkout.html",
        {
            "request": request,
            "order": order,
            "client_key": settings.TOSS_CLIENT_KEY,
            "success_url": f"{settings.BASE_URL}/payment/success",
            "fail_url": f"{settings.BASE_URL}/payment/fail"
        }
    )


@router.get("/success")
async def payment_success(
    request: Request,
    paymentKey: str,
    orderId: str,
    amount: int,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    user: User = Depends(get_current_user)
):
    """결제 성공 (리다이렉트)"""
    # 주문 조회
    order = order_crud.get_order_by_number(session, orderId)
    if not order:
        return templates.TemplateResponse(
            "payment/fail.html",
            {"request": request, "message": "주문을 찾을 수 없습니다"}
        )

    # 권한 확인
    if order.user_id != user.id:
        return templates.TemplateResponse(
            "payment/fail.html",
            {"request": request, "message": "접근 권한이 없습니다"}
        )

    # 금액 확인
    if order.final_price != amount:
        return templates.TemplateResponse(
            "payment/fail.html",
            {"request": request, "message": "결제 금액이 일치하지 않습니다"}
        )

    # 결제 승인
    result = await confirm_payment(paymentKey, orderId, amount)

    if not result["success"]:
        error = result["error"]
        return templates.TemplateResponse(
            "payment/fail.html",
            {
                "request": request,
                "message": error.get("message", "결제 승인에 실패했습니다"),
                "code": error.get("code")
            }
        )

    # 결제 정보 업데이트
    payment_data = result["data"]
    payment = order.payment
    payment.payment_key = paymentKey
    payment.status = PaymentStatus.COMPLETED
    payment.method = payment_data.get("method")
    payment.receipt_url = payment_data.get("receipt", {}).get("url")
    payment.completed_at = datetime.now()
    session.add(payment)

    # 주문 상태 업데이트
    order_crud.update_order_status(session, order, OrderStatus.PAID)

    return templates.TemplateResponse(
        "payment/success.html",
        {"request": request, "order": order}
    )


@router.get("/fail")
async def payment_fail(
    request: Request,
    code: str = None,
    message: str = None,
    orderId: str = None,
    templates=Depends(get_templates)
):
    """결제 실패 (리다이렉트)"""
    return templates.TemplateResponse(
        "payment/fail.html",
        {
            "request": request,
            "code": code,
            "message": message or "결제가 실패했습니다",
            "order_id": orderId
        }
    )
