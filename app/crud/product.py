from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models import Product, ProductCreate, ProductUpdate, Category


def create_product(session: Session, product_create: ProductCreate) -> Product:
    """상품 생성"""
    product = Product.model_validate(product_create)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def get_products(
    session: Session,
    category_id: int | None = None,
    active_only: bool = True,
    featured_only: bool = False,
    skip: int = 0,
    limit: int = 20
) -> list[Product]:
    """상품 목록"""
    statement = (
        select(Product)
        .options(selectinload(Product.category))
        .options(selectinload(Product.images))
        .order_by(Product.created_at.desc())
    )

    if active_only:
        statement = statement.where(Product.is_active == True)
    if featured_only:
        statement = statement.where(Product.is_featured == True)
    if category_id:
        statement = statement.where(Product.category_id == category_id)

    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def get_product(session: Session, product_id: int) -> Product | None:
    """상품 조회"""
    statement = (
        select(Product)
        .options(selectinload(Product.category))
        .options(selectinload(Product.images))
        .where(Product.id == product_id)
    )
    return session.exec(statement).first()


def get_product_by_slug(session: Session, slug: str) -> Product | None:
    """슬러그로 상품 조회"""
    statement = (
        select(Product)
        .options(selectinload(Product.category))
        .options(selectinload(Product.images))
        .where(Product.slug == slug)
    )
    return session.exec(statement).first()


def update_product(
    session: Session,
    product: Product,
    product_update: ProductUpdate
) -> Product:
    """상품 수정"""
    from datetime import datetime
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    product.updated_at = datetime.now()
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def delete_product(session: Session, product: Product) -> None:
    """상품 삭제"""
    session.delete(product)
    session.commit()


def count_products(
    session: Session,
    category_id: int | None = None,
    active_only: bool = True
) -> int:
    """상품 수"""
    statement = select(Product)
    if active_only:
        statement = statement.where(Product.is_active == True)
    if category_id:
        statement = statement.where(Product.category_id == category_id)
    return len(session.exec(statement).all())


def search_products(
    session: Session,
    query: str,
    skip: int = 0,
    limit: int = 20
) -> list[Product]:
    """상품 검색"""
    statement = (
        select(Product)
        .options(selectinload(Product.category))
        .where(
            Product.is_active == True,
            Product.name.contains(query) | Product.description.contains(query)
        )
        .order_by(Product.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()
