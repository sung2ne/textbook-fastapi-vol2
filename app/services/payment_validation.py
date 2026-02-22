from app.models import Order


class PaymentValidationError(Exception):
    pass


def validate_payment(order: Order, amount: int, user_id: int) -> None:
    """결제 검증"""
    # 주문자 확인
    if order.user_id != user_id:
        raise PaymentValidationError("주문자가 일치하지 않습니다")

    # 금액 확인
    if order.final_price != amount:
        raise PaymentValidationError("결제 금액이 일치하지 않습니다")

    # 주문 상태 확인
    from app.models import OrderStatus
    if order.status != OrderStatus.PENDING:
        raise PaymentValidationError("이미 처리된 주문입니다")
