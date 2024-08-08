FROM mysql:latest

# MySQL 설정 파일을 컨테이너의 설정 디렉토리로 복사(한글설정)
COPY ./init/init.cnf /etc/mysql/conf.d/

# SQL 초기화 스크립트 및 필요한 파일 복사
COPY ./init /docker-entrypoint-initdb.d

# 권한 설정
RUN chmod 644 /etc/mysql/conf.d/init.cnf && \
    chmod -R 755 /docker-entrypoint-initdb.d

# 포트 설정 (필요시)
EXPOSE 3306

# 파일 복사 및 MySQL 서버 시작
CMD ["bash", "-c", "cp -r /docker-entrypoint-initdb.d/shared_files/* /shared_files/ && exec docker-entrypoint.sh mysqld"]