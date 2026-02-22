from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class Cart(SQLModel, table=True):
    """장바구니 테이블"""
    __tablename__ = "carts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id")
    session_id: str | None = Field(default=None, index=True)  # 비회원용
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None

    # 관계
    user: "User" = Relationship()
    items: list["CartItem"] = Relationship(
        back_populates="cart",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def total_price(self) -> int:
        """총 금액"""
        return sum(item.subtotal for item in self.items)

    @property
    def total_quantity(self) -> int:
        """총 수량"""
        return sum(item.quantity for item in self.items)


class CartItem(SQLModel, table=True):
    """장바구니 상품 테이블"""
    __tablename__ = "cart_items"

    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=datetime.now)

    # 관계
    cart: Cart = Relationship(back_populates="items")
    product: "Product" = Relationship()

    @property
    def subtotal(self) -> int:
        """소계"""
        return self.product.price * self.quantity
