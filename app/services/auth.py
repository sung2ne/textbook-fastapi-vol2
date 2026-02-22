from sqlmodel import Session
from app.models import User, UserCreate, UserLogin
from app.crud import user as user_crud
from app.services.password import hash_password, verify_password, validate_password, PasswordError


class AuthError(Exception):
    """인증 오류"""
    pass


def register_user(session: Session, user_create: UserCreate) -> User:
    """회원가입"""
    # 이메일 중복 확인
    existing = user_crud.get_user_by_email(session, user_create.email)
    if existing:
        raise AuthError("이미 사용 중인 이메일입니다")

    # 비밀번호 정책 확인
    try:
        validate_password(user_create.password)
    except PasswordError as e:
        raise AuthError(str(e))

    # 비밀번호 해싱
    hashed_password = hash_password(user_create.password)

    # 회원 생성
    return user_crud.create_user(session, user_create, hashed_password)


def authenticate_user(session: Session, user_login: UserLogin) -> User:
    """로그인 인증"""
    user = user_crud.get_user_by_email(session, user_login.email)

    if not user:
        raise AuthError("이메일 또는 비밀번호가 올바르지 않습니다")

    if not verify_password(user_login.password, user.hashed_password):
        raise AuthError("이메일 또는 비밀번호가 올바르지 않습니다")

    if not user.is_active:
        raise AuthError("비활성화된 계정입니다")

    # 마지막 로그인 시간 업데이트
    user_crud.update_last_login(session, user)

    return user
