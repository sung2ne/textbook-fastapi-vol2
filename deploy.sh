#!/bin/bash

set -e

echo "=== FastAPI 쇼핑몰 배포 시작 ==="

# 환경 변수 파일 확인
if [ ! -f ".env.prod" ]; then
    echo "오류: .env.prod 파일이 없습니다"
    echo "cp .env.prod.example .env.prod 후 설정해주세요"
    exit 1
fi

# 환경 변수 로드
export $(cat .env.prod | grep -v '^#' | xargs)

echo "1. 이미지 빌드 중..."
docker-compose -f docker-compose.prod.yml build

echo "2. 데이터베이스 마이그레이션..."
docker-compose -f docker-compose.prod.yml run --rm app alembic upgrade head

echo "3. 서비스 시작..."
docker-compose -f docker-compose.prod.yml up -d

echo "4. 상태 확인..."
docker-compose -f docker-compose.prod.yml ps

echo "=== 배포 완료 ==="
echo "쇼핑몰: $BASE_URL"
