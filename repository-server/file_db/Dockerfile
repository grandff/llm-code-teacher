FROM mysql:latest

# SQL 초기화 스크립트 및 필요한 파일 복사
COPY ./init /docker-entrypoint-initdb.d

# 권한 설정
RUN chmod -R 755 /docker-entrypoint-initdb.d

# 포트 설정 (필요시)
EXPOSE 3306