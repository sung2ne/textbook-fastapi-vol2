from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_templates, get_current_admin_user
from app.crud import order as order_crud
from app.services.toss import cancel_payment
from app.models import OrderStatus, PaymentStatus

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


@router.get("")
async def order_list(
    request: Request,
    status: str | None = None,
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """주문 목록"""
    per_page = 20
    skip = (page - 1) * per_page

    # 상태 필터
    order_status = None
    if status:
        try:
            order_status = OrderStatus(status)
        except ValueError:
            pass

    orders = order_crud.get_all_orders(session, status=order_status, skip=skip, limit=per_page)
    total = order_crud.count_orders(session, status=order_status)

    # 상태별 카운트
    status_counts = {
        "all": order_crud.count_orders(session),
        "pending": order_crud.count_orders(session, OrderStatus.PENDING),
        "paid": order_crud.count_orders(session, OrderStatus.PAID),
        "preparing": order_crud.count_orders(session, OrderStatus.PREPARING),
        "shipping": order_crud.count_orders(session, OrderStatus.SHIPPING),
        "delivered": order_crud.count_orders(session, OrderStatus.DELIVERED),
        "cancelled": order_crud.count_orders(session, OrderStatus.CANCELLED),
    }

    return templates.TemplateResponse(
        "admin/orders/list.html",
        {
            "request": request,
            "orders": orders,
            "status": status,
            "status_counts": status_counts,
            "page": page,
            "total": total,
            "per_page": per_page
        }
    )


@router.get("/{order_id}")
async def order_detail(
    request: Request,
    order_id: int,
    session: Session = Depends(get_session),
    templates=Depends(get_templates),
    admin=Depends(get_current_admin_user)
):
    """주문 상세"""
    order = order_crud.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    return templates.TemplateResponse(
        "admin/orders/detail.html",
        {"request": request, "order": order}
    )


@router.post("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str = Form(...),
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """주문 상태 변경"""
    order = order_crud.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    try:
        new_status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 상태입니다")

    order_crud.update_order_status(session, order, new_status)

    return RedirectResponse(url=f"/admin/orders/{order_id}", status_code=303)


@router.post("/{order_id}/cancel")
async def admin_cancel_order(
    order_id: int,
    cancel_reason: str = Form(...),
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin_user)
):
    """관리자 주문 취소"""
    order = order_crud.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    # 결제 취소
    if order.payment and order.payment.payment_key:
        result = await cancel_payment(order.payment.payment_key, cancel_reason)

        if not result["success"]:
            error = result["error"]
            raise HTTPException(
                status_code=400,
                detail=f"결제 취소 실패: {error.get('message')}"
            )

        order.payment.status = PaymentStatus.CANCELLED
        session.add(order.payment)

    # 주문 취소
    order_crud.cancel_order(session, order)

    return RedirectResponse(url=f"/admin/orders/{order_id}", status_code=303)
