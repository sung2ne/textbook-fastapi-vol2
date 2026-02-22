from sqlmodel import Session
from app.models import Cart, CartItem
from app.crud import product as product_crud


class CartValidationError(Exception):
    def __init__(self, errors: list[dict]):
        self.errors = errors


def validate_cart(session: Session, cart: Cart) -> None:
    """장바구니 검증"""
    errors = []

    for item in cart.items:
        product = product_crud.get_product(session, item.product_id)

        if not product:
            errors.append({
                "item_id": item.id,
                "message": f"'{item.product.name}' 상품이 존재하지 않습니다"
            })
            continue

        if not product.is_active:
            errors.append({
                "item_id": item.id,
                "message": f"'{product.name}' 상품이 판매 중지되었습니다"
            })
            continue

        if product.stock < item.quantity:
            errors.append({
                "item_id": item.id,
                "message": f"'{product.name}' 재고가 부족합니다 (재고: {product.stock}개)"
            })

    if errors:
        raise CartValidationError(errors)
