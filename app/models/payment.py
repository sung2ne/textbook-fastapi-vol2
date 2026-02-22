from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.order import Order


class PaymentMethod(str, Enum):
    """결제 수단"""
    CARD = "card"           # 카드
    TRANSFER = "transfer"   # 계좌이체
    VIRTUAL = "virtual"     # 가상계좌
    PHONE = "phone"         # 휴대폰


class PaymentStatus(str, Enum):
    """결제 상태"""
    PENDING = "pending"      # 대기
    COMPLETED = "completed"  # 완료
    FAILED = "failed"        # 실패
    CANCELLED = "cancelled"  # 취소


class Payment(SQLModel, table=True):
    """결제 테이블"""
    __tablename__ = "payments"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", unique=True)

    # 결제 정보
    method: PaymentMethod | None = None
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    amount: int  # 결제 금액

    # PG사 정보 (토스페이먼츠)
    payment_key: str | None = None  # PG사 결제 키
    receipt_url: str | None = None  # 영수증 URL

    # 시간
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # 관계
    order: "Order" = Relationship(back_populates="payment")
