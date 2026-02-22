from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.payment import Payment


class OrderStatus(str, Enum):
    """주문 상태"""
    PENDING = "pending"          # 결제 대기
    PAID = "paid"                # 결제 완료
    PREPARING = "preparing"      # 배송 준비
    SHIPPING = "shipping"        # 배송 중
    DELIVERED = "delivered"      # 배송 완료
    CANCELLED = "cancelled"      # 취소


class Order(SQLModel, table=True):
    """주문 테이블"""
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True)  # 주문번호
    user_id: int = Field(foreign_key="users.id")

    # 주문 정보
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_price: int  # 상품 금액
    shipping_fee: int = 0  # 배송비
    final_price: int  # 최종 결제 금액

    # 배송 정보
    recipient: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    zipcode: str = Field(max_length=10)
    address1: str = Field(max_length=200)
    address2: str | None = Field(default=None, max_length=200)
    memo: str | None = None  # 배송 메모

    # 시간
    created_at: datetime = Field(default_factory=datetime.now)
    paid_at: datetime | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    cancelled_at: datetime | None = None

    # 관계
    user: "User" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    payment: "Payment" = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """주문 상품 테이블"""
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")

    # 주문 당시 정보 (상품 정보가 변경되어도 주문 내역은 유지)
    product_name: str
    product_price: int
    quantity: int
    subtotal: int

    # 관계
    order: Order = Relationship(back_populates="items")
    product: "Product" = Relationship()
