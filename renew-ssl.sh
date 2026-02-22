#!/bin/bash

# Nginx 중지
docker-compose -f docker-compose.prod.yml stop nginx

# 인증서 갱신
certbot renew

# Nginx 시작
docker-compose -f docker-compose.prod.yml start nginx

echo "SSL 인증서 갱신 완료"
