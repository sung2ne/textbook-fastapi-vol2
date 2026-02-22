from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from app.models.order import Order


class UserRole(str, Enum):
    """회원 역할"""
    USER = "user"
    ADMIN = "admin"


class UserBase(SQLModel):
    """회원 기본"""
    email: str = Field(max_length=255, unique=True, index=True)
    name: str = Field(max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class User(UserBase, table=True):
    """회원 테이블"""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_login_at: datetime | None = None

    # 관계
    orders: list["Order"] = Relationship(back_populates="user")
    addresses: list["Address"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """회원가입"""
    email: str
    password: str
    name: str
    phone: str | None = None


class UserUpdate(SQLModel):
    """회원정보 수정"""
    name: str | None = None
    phone: str | None = None


class UserLogin(SQLModel):
    """로그인"""
    email: str
    password: str


class AddressBase(SQLModel):
    """배송지 기본"""
    name: str = Field(max_length=50)
    recipient: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    zipcode: str = Field(max_length=10)
    address1: str = Field(max_length=200)
    address2: str | None = Field(default=None, max_length=200)
    is_default: bool = False


class Address(AddressBase, table=True):
    """배송지 테이블"""
    __tablename__ = "addresses"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)

    # 관계
    user: User = Relationship(back_populates="addresses")


class AddressCreate(AddressBase):
    """배송지 생성"""
    pass


class AddressUpdate(SQLModel):
    """배송지 수정"""
    name: str | None = None
    recipient: str | None = None
    phone: str | None = None
    zipcode: str | None = None
    address1: str | None = None
    address2: str | None = None
    is_default: bool | None = None
