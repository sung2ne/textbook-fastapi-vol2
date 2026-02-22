# 소설처럼 읽는 FastAPI Vol.2 - 쇼핑몰

FastAPI + Jinja2 + SQLModel + PostgreSQL로 만든 쇼핑몰 프로젝트입니다.

## 기술 스택

- **Backend**: FastAPI 0.129.2
- **Template**: Jinja2
- **ORM**: SQLModel 0.0.37
- **Database**: PostgreSQL
- **Cache**: Redis
- **Payment**: 토스페이먼츠
- **Deploy**: Docker + Nginx

## 브랜치 구조

각 챕터별로 브랜치가 생성되어 있습니다.

- `part01/chapter-01` ~ `part09/chapter-04`

## 빠른 시작

```bash
# 1. 환경 설정
cp .env.example .env
# .env 파일 수정

# 2. 데이터베이스 실행
docker-compose up -d db redis

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 마이그레이션
alembic upgrade head

# 5. 관리자 계정 생성
python -m app.cli create-admin

# 6. 앱 실행
uvicorn app.main:app --reload
```

## 프로덕션 배포

```bash
cp .env.prod.example .env.prod
# .env.prod 수정 후

./deploy.sh
```

## 폴더 구조

```
app/
├── models/          # SQLModel 모델
├── crud/            # CRUD 함수
├── routers/         # FastAPI 라우터
│   └── admin/       # 관리자 라우터
├── services/        # 비즈니스 로직
├── templates/       # Jinja2 템플릿
│   └── admin/       # 관리자 템플릿
├── static/          # 정적 파일
├── config.py        # 설정
├── database.py      # DB 연결
├── dependencies.py  # 의존성
└── main.py          # 앱 진입점
```
