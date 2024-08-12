# MariaDB 최신 이미지를 기반으로 사용
FROM mariadb:10.6

# SQL 초기화 스크립트 및 필요한 파일 복사
COPY ./init /docker-entrypoint-initdb.d

# 포트 설정 (필요시)
EXPOSE 3306

# MariaDB 서버 시작 전 init.sh 실행
CMD ["bash", "/docker-entrypoint-initdb.d/init.sh"]