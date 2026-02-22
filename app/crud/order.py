from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models import Order, OrderItem, OrderStatus, Payment


def create_order(
    session: Session,
    user_id: int,
    order_number: str,
    total_price: int,
    shipping_fee: int,
    recipient: str,
    phone: str,
    zipcode: str,
    address1: str,
    address2: str | None,
    memo: str | None,
    cart_items: list
) -> Order:
    """주문 생성"""
    # 주문 생성
    order = Order(
        order_number=order_number,
        user_id=user_id,
        total_price=total_price,
        shipping_fee=shipping_fee,
        final_price=total_price + shipping_fee,
        recipient=recipient,
        phone=phone,
        zipcode=zipcode,
        address1=address1,
        address2=address2,
        memo=memo
    )
    session.add(order)
    session.flush()  # ID 생성

    # 주문 상품 생성
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name,
            product_price=item.product.price,
            quantity=item.quantity,
            subtotal=item.subtotal
        )
        session.add(order_item)

    # 결제 정보 생성
    payment = Payment(
        order_id=order.id,
        amount=order.final_price
    )
    session.add(payment)

    session.commit()
    session.refresh(order)
    return order


def get_order(session: Session, order_id: int) -> Order | None:
    """주문 조회"""
    statement = select(Order).options(
        selectinload(Order.items),
        selectinload(Order.payment)
    ).where(Order.id == order_id)
    return session.exec(statement).first()


def get_order_by_number(session: Session, order_number: str) -> Order | None:
    """주문번호로 조회"""
    statement = select(Order).options(
        selectinload(Order.items),
        selectinload(Order.payment)
    ).where(Order.order_number == order_number)
    return session.exec(statement).first()


def get_user_orders(
    session: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> list[Order]:
    """회원 주문 목록"""
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def update_order_status(
    session: Session,
    order: Order,
    status: OrderStatus
) -> Order:
    """주문 상태 변경"""
    order.status = status

    # 상태별 시간 기록
    now = datetime.now()
    if status == OrderStatus.PAID:
        order.paid_at = now
    elif status == OrderStatus.SHIPPING:
        order.shipped_at = now
    elif status == OrderStatus.DELIVERED:
        order.delivered_at = now
    elif status == OrderStatus.CANCELLED:
        order.cancelled_at = now

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def cancel_order(session: Session, order: Order) -> Order:
    """주문 취소"""
    from app.crud import product as product_crud

    # 재고 복구
    for item in order.items:
        product = product_crud.get_product(session, item.product_id)
        if product:
            product.stock += item.quantity
            session.add(product)

    # 상태 변경
    order = update_order_status(session, order, OrderStatus.CANCELLED)

    return order


def get_all_orders(
    session: Session,
    status: OrderStatus | None = None,
    skip: int = 0,
    limit: int = 20
) -> list[Order]:
    """전체 주문 목록 (관리자용)"""
    statement = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.user))
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    if status:
        statement = statement.where(Order.status == status)

    return session.exec(statement).all()
