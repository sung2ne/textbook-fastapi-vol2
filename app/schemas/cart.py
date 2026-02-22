from pydantic import BaseModel


class AddToCartRequest(BaseModel):
    """장바구니 담기 요청"""
    product_id: int
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    """수량 변경 요청"""
    quantity: int


class CartItemResponse(BaseModel):
    """장바구니 상품 응답"""
    id: int
    product_id: int
    product_name: str
    product_image: str
    price: int
    quantity: int
    subtotal: int


class CartResponse(BaseModel):
    """장바구니 응답"""
    items: list[CartItemResponse]
    total_price: int
    total_quantity: int
