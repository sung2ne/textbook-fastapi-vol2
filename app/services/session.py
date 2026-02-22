from fastapi import Request, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature
from app.config import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

SESSION_COOKIE = "session"
MAX_AGE = 60 * 60 * 24 * 7  # 7일


def create_session(response: Response, user_id: int) -> None:
    """세션 생성"""
    token = serializer.dumps({"user_id": user_id})
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=MAX_AGE,
        httponly=True,
        samesite="lax"
    )


def get_session(request: Request) -> dict | None:
    """세션 조회"""
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None

    try:
        data = serializer.loads(token, max_age=MAX_AGE)
        return data
    except BadSignature:
        return None


def destroy_session(response: Response) -> None:
    """세션 삭제"""
    response.delete_cookie(SESSION_COOKIE)
