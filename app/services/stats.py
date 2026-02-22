from datetime import datetime, timedelta
from sqlmodel import Session, select, func
from app.models import Order, OrderStatus, User, Product


def get_dashboard_stats(session: Session) -> dict:
    """대시보드 통계"""
    today = datetime.now().date()
    start_of_month = today.replace(day=1)

    return {
        "orders": get_order_stats(session, today, start_of_month),
        "revenue": get_revenue_stats(session, today, start_of_month),
        "users": get_user_stats(session, today, start_of_month),
        "products": get_product_stats(session)
    }


def get_order_stats(session: Session, today, start_of_month) -> dict:
    """주문 통계"""
    # 오늘 주문
    today_orders = session.exec(
        select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
    ).one()

    # 이번 달 주문
    month_orders = session.exec(
        select(func.count(Order.id)).where(
            Order.created_at >= start_of_month
        )
    ).one()

    # 처리 대기 주문
    pending_orders = session.exec(
        select(func.count(Order.id)).where(
            Order.status.in_([OrderStatus.PAID, OrderStatus.PREPARING])
        )
    ).one()

    return {
        "today": today_orders,
        "month": month_orders,
        "pending": pending_orders
    }


def get_revenue_stats(session: Session, today, start_of_month) -> dict:
    """매출 통계"""
    # 오늘 매출
    today_revenue = session.exec(
        select(func.coalesce(func.sum(Order.final_price), 0)).where(
            func.date(Order.paid_at) == today,
            Order.status != OrderStatus.CANCELLED
        )
    ).one()

    # 이번 달 매출
    month_revenue = session.exec(
        select(func.coalesce(func.sum(Order.final_price), 0)).where(
            Order.paid_at >= start_of_month,
            Order.status != OrderStatus.CANCELLED
        )
    ).one()

    return {
        "today": today_revenue,
        "month": month_revenue
    }


def get_user_stats(session: Session, today, start_of_month) -> dict:
    """회원 통계"""
    # 전체 회원
    total_users = session.exec(select(func.count(User.id))).one()

    # 오늘 가입
    today_users = session.exec(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    ).one()

    return {
        "total": total_users,
        "today": today_users
    }


def get_product_stats(session: Session) -> dict:
    """상품 통계"""
    # 전체 상품
    total_products = session.exec(select(func.count(Product.id))).one()

    # 재고 부족 (10개 미만)
    low_stock = session.exec(
        select(func.count(Product.id)).where(
            Product.stock < 10,
            Product.is_active == True
        )
    ).one()

    return {
        "total": total_products,
        "low_stock": low_stock
    }


def get_recent_orders(session: Session, limit: int = 10) -> list:
    """최근 주문"""
    statement = (
        select(Order)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()


def get_sales_chart_data(session: Session, days: int = 7) -> dict:
    """일별 매출 차트 데이터"""
    today = datetime.now().date()
    labels = []
    data = []

    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        labels.append(date.strftime("%m/%d"))

        revenue = session.exec(
            select(func.coalesce(func.sum(Order.final_price), 0)).where(
                func.date(Order.paid_at) == date,
                Order.status != OrderStatus.CANCELLED
            )
        ).one()
        data.append(int(revenue))

    return {"labels": labels, "data": data}
