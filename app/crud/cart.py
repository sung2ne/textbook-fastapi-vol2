from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models import Cart, CartItem, Product


def get_or_create_cart(
    session: Session,
    user_id: int | None = None,
    session_id: str | None = None
) -> Cart:
    """장바구니 조회 또는 생성"""
    statement = select(Cart).options(
        selectinload(Cart.items).selectinload(CartItem.product)
    )

    if user_id:
        statement = statement.where(Cart.user_id == user_id)
    elif session_id:
        statement = statement.where(Cart.session_id == session_id)
    else:
        raise ValueError("user_id 또는 session_id가 필요합니다")

    cart = session.exec(statement).first()

    if not cart:
        cart = Cart(user_id=user_id, session_id=session_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    return cart


def add_to_cart(
    session: Session,
    cart: Cart,
    product_id: int,
    quantity: int = 1
) -> CartItem:
    """장바구니에 상품 추가"""
    # 이미 담긴 상품인지 확인
    statement = select(CartItem).where(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    )
    item = session.exec(statement).first()

    if item:
        # 수량 추가
        item.quantity += quantity
    else:
        # 새로 추가
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        session.add(item)

    # 장바구니 업데이트 시간
    cart.updated_at = datetime.now()
    session.add(cart)
    session.commit()
    session.refresh(item)

    return item


def update_cart_item(
    session: Session,
    item_id: int,
    quantity: int
) -> CartItem | None:
    """장바구니 상품 수량 변경"""
    item = session.get(CartItem, item_id)
    if not item:
        return None

    if quantity <= 0:
        session.delete(item)
        session.commit()
        return None

    item.quantity = quantity
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def remove_from_cart(session: Session, item_id: int) -> bool:
    """장바구니에서 상품 삭제"""
    item = session.get(CartItem, item_id)
    if not item:
        return False

    session.delete(item)
    session.commit()
    return True


def clear_cart(session: Session, cart: Cart) -> None:
    """장바구니 비우기"""
    for item in cart.items:
        session.delete(item)
    session.commit()


def get_cart_item(session: Session, item_id: int) -> CartItem | None:
    """장바구니 상품 조회"""
    statement = select(CartItem).options(
        selectinload(CartItem.product)
    ).where(CartItem.id == item_id)
    return session.exec(statement).first()


def merge_carts(
    session: Session,
    user_cart: Cart,
    guest_cart: Cart
) -> None:
    """비회원 장바구니를 회원 장바구니로 병합"""
    for guest_item in guest_cart.items:
        # 회원 장바구니에 같은 상품이 있는지 확인
        user_item = None
        for item in user_cart.items:
            if item.product_id == guest_item.product_id:
                user_item = item
                break

        if user_item:
            # 수량 합치기
            user_item.quantity += guest_item.quantity
            session.add(user_item)
        else:
            # 새로 추가
            new_item = CartItem(
                cart_id=user_cart.id,
                product_id=guest_item.product_id,
                quantity=guest_item.quantity
            )
            session.add(new_item)

    # 비회원 장바구니 삭제
    session.delete(guest_cart)
    session.commit()
