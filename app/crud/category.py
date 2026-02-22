from sqlmodel import Session, select
from app.models import Category, CategoryCreate, CategoryUpdate


def create_category(session: Session, category_create: CategoryCreate) -> Category:
    """카테고리 생성"""
    category = Category.model_validate(category_create)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_categories(
    session: Session,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
) -> list[Category]:
    """카테고리 목록"""
    statement = select(Category).order_by(Category.sort_order)
    if active_only:
        statement = statement.where(Category.is_active == True)
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def get_category(session: Session, category_id: int) -> Category | None:
    """카테고리 조회"""
    return session.get(Category, category_id)


def get_category_by_slug(session: Session, slug: str) -> Category | None:
    """슬러그로 카테고리 조회"""
    statement = select(Category).where(Category.slug == slug)
    return session.exec(statement).first()


def update_category(
    session: Session,
    category: Category,
    category_update: CategoryUpdate
) -> Category:
    """카테고리 수정"""
    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category: Category) -> None:
    """카테고리 삭제"""
    session.delete(category)
    session.commit()
