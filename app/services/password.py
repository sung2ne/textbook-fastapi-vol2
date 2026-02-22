import re
from passlib.context import CryptContext

# bcrypt 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


class PasswordError(Exception):
    """비밀번호 오류"""
    pass


def validate_password(password: str) -> None:
    """
    비밀번호 정책 검증
    - 최소 8자
    - 영문, 숫자 포함
    """
    if len(password) < 8:
        raise PasswordError("비밀번호는 8자 이상이어야 합니다")

    if not re.search(r"[A-Za-z]", password):
        raise PasswordError("비밀번호에 영문자를 포함해야 합니다")

    if not re.search(r"\d", password):
        raise PasswordError("비밀번호에 숫자를 포함해야 합니다")
