from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

# 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 디버그 모드에서 SQL 출력
)


def create_db_and_tables():
    """테이블 생성 (개발용)"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """세션 의존성"""
    with Session(engine) as session:
        yield session
