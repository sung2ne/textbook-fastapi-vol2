from sqlmodel import Session, select, func
from app.models import User, UserCreate, Address, AddressCreate, UserRole


def get_user_by_email(session: Session, email: str) -> User | None:
    """이메일로 회원 조회"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user(session: Session, user_id: int) -> User | None:
    """ID로 회원 조회"""
    return session.get(User, user_id)


def create_user(session: Session, user_create: UserCreate, hashed_password: str) -> User:
    """회원 생성"""
    user = User(
        email=user_create.email,
        name=user_create.name,
        phone=user_create.phone,
        hashed_password=hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_last_login(session: Session, user: User) -> None:
    """마지막 로그인 시간 업데이트"""
    from datetime import datetime
    user.last_login_at = datetime.now()
    session.add(user)
    session.commit()


def get_user_addresses(session: Session, user_id: int) -> list[Address]:
    """회원 배송지 목록"""
    statement = select(Address).where(Address.user_id == user_id)
    return session.exec(statement).all()


def create_address(session: Session, user_id: int, address_create: AddressCreate) -> Address:
    """배송지 생성"""
    if address_create.is_default:
        statement = select(Address).where(
            Address.user_id == user_id,
            Address.is_default == True
        )
        for addr in session.exec(statement).all():
            addr.is_default = False
            session.add(addr)

    address = Address(user_id=user_id, **address_create.model_dump())
    session.add(address)
    session.commit()
    session.refresh(address)
    return address


def get_all_users(
    session: Session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20
) -> list[User]:
    """전체 회원 목록"""
    statement = select(User).order_by(User.created_at.desc())

    if search:
        statement = statement.where(
            User.email.contains(search) | User.name.contains(search)
        )

    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def count_users(session: Session, search: str | None = None) -> int:
    """회원 수"""
    statement = select(func.count(User.id))
    if search:
        statement = statement.where(
            User.email.contains(search) | User.name.contains(search)
        )
    return session.exec(statement).one()


def update_user_status(session: Session, user: User, is_active: bool) -> User:
    """회원 상태 변경"""
    user.is_active = is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user_role(session: Session, user: User, role: UserRole) -> User:
    """회원 역할 변경"""
    user.role = role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
