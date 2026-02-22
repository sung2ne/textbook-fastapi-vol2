#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=${BACKUP_DIR:-/backups}

# 백업 폴더 생성
mkdir -p $BACKUP_DIR

# 백업
docker exec shop-db pg_dump -U shop shop > $BACKUP_DIR/shop_$DATE.sql

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "shop_*.sql" -mtime +7 -delete

echo "백업 완료: $BACKUP_DIR/shop_$DATE.sql"
