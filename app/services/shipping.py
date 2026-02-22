FREE_SHIPPING_THRESHOLD = 50000  # 무료배송 기준
SHIPPING_FEE = 3000  # 기본 배송비


def calculate_shipping_fee(total_price: int) -> int:
    """배송비 계산"""
    if total_price >= FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING_FEE


def get_free_shipping_remaining(total_price: int) -> int:
    """무료배송까지 남은 금액"""
    if total_price >= FREE_SHIPPING_THRESHOLD:
        return 0
    return FREE_SHIPPING_THRESHOLD - total_price
