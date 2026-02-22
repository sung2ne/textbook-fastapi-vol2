# 소설처럼 읽는 FastAPI Vol.2

Jinja2 템플릿으로 배우는 FastAPI 웹 개발 (쇼핑몰)

## 실습 코드 저장소

이 저장소는 교재 "소설처럼 읽는 FastAPI Vol.2"의 실습 코드를 챕터별로 관리합니다.

## 브랜치 구조

각 브랜치는 해당 챕터까지의 코드가 누적 적용되어 있습니다.

- `part01/chapter-01` ~ `part09/chapter-04` (38개 브랜치)

## 실행 방법

```bash
git clone https://github.com/sung2ne/textbook-fastapi-vol2.git
cd textbook-fastapi-vol2

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

docker-compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

## 교재 링크

https://wikidocs.net/book/18956
