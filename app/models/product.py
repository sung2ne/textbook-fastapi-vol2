from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.category import Category


class ProductBase(SQLModel):
    """상품 기본"""
    name: str = Field(max_length=200)
    slug: str = Field(max_length=200, unique=True, index=True)
    description: str | None = None
    price: int = Field(ge=0)  # 원 단위
    original_price: int | None = None  # 원래 가격 (할인 표시용)
    stock: int = Field(default=0, ge=0)
    is_active: bool = True
    is_featured: bool = False  # 추천 상품


class Product(ProductBase, table=True):
    """상품 테이블"""
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None

    # 관계
    category: "Category" = Relationship(back_populates="products")
    images: list["ProductImage"] = Relationship(back_populates="product")

    @property
    def discount_percent(self) -> int | None:
        """할인율 계산"""
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return None

    @property
    def main_image(self) -> str:
        """대표 이미지"""
        if self.images:
            return self.images[0].url
        return "/static/images/no-image.png"


class ProductCreate(ProductBase):
    """상품 생성"""
    category_id: int


class ProductUpdate(SQLModel):
    """상품 수정"""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: int | None = None
    original_price: int | None = None
    stock: int | None = None
    category_id: int | None = None
    is_active: bool | None = None
    is_featured: bool | None = None


class ProductImage(SQLModel, table=True):
    """상품 이미지 테이블"""
    __tablename__ = "product_images"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    url: str
    alt: str | None = None
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    # 관계
    product: Product = Relationship(back_populates="images")
