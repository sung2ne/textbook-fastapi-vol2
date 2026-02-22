from datetime import datetime, timedelta
from app.models import Order, OrderStatus


class RefundPolicy:
    """환불 정책"""

    @staticmethod
    def can_full_refund(order: Order) -> bool:
        """전액 환불 가능 여부"""
        # 결제 완료 후 7일 이내
        if order.paid_at:
            deadline = order.paid_at + timedelta(days=7)
            return datetime.now() < deadline
        return True

    @staticmethod
    def get_refund_amount(order: Order) -> int:
        """환불 금액 계산"""
        if RefundPolicy.can_full_refund(order):
            return order.final_price

        # 7일 이후 배송비 제외
        return order.total_price

    @staticmethod
    def get_cancel_message(order: Order) -> str:
        """취소 안내 메시지"""
        if order.status == OrderStatus.SHIPPING:
            return "배송 중인 상품은 취소할 수 없습니다. 반품을 신청해주세요."
        if order.status == OrderStatus.DELIVERED:
            return "배송 완료된 상품은 반품을 신청해주세요."
        return ""
