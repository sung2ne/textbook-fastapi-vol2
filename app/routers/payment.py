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
