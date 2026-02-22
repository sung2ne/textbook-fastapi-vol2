import uuid
from fastapi import Request, Response

CART_SESSION_COOKIE = "cart_session"
MAX_AGE = 60 * 60 * 24 * 30  # 30일


def get_cart_session_id(request: Request) -> str | None:
    """장바구니 세션 ID 조회"""
    return request.cookies.get(CART_SESSION_COOKIE)


def create_cart_session_id() -> str:
    """새 세션 ID 생성"""
    return str(uuid.uuid4())


def set_cart_session_cookie(response: Response, session_id: str) -> None:
    """세션 쿠키 설정"""
    response.set_cookie(
        key=CART_SESSION_COOKIE,
        value=session_id,
        max_age=MAX_AGE,
        httponly=True,
        samesite="lax"
    )


def clear_cart_session_cookie(response: Response) -> None:
    """세션 쿠키 삭제"""
    response.delete_cookie(CART_SESSION_COOKIE)
