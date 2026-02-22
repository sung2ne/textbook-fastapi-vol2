from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product


class CategoryBase(SQLModel):
    """카테고리 기본"""
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50, unique=True, index=True)
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0


class Category(CategoryBase, table=True):
    """카테고리 테이블"""
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None

    # 관계
    products: list["Product"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    """카테고리 생성"""
    pass


class CategoryUpdate(SQLModel):
    """카테고리 수정"""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None
