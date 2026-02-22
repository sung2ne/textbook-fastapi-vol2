from sqlmodel import Session
from app.models import Order, User


class OrderAccessError(Exception):
    pass


def validate_order_access(session: Session, order: Order, user: User) -> None:
    """주문 접근 권한 검증"""
    if order.user_id != user.id:
        raise OrderAccessError("접근 권한이 없습니다")


def validate_order_cancellable(order: Order) -> None:
    """취소 가능 여부 검증"""
    from app.models import OrderStatus

    non_cancellable = [
        OrderStatus.SHIPPING,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED
    ]

    if order.status in non_cancellable:
        raise OrderAccessError("취소할 수 없는 주문입니다")
