#!/bin/bash

# MariaDB의 초기화 작업 수행
echo "Performing initial setup..."

# 권한 설정
chmod -R 755 /docker-entrypoint-initdb.d
chown -R mysql:mysql /docker-entrypoint-initdb.d

# 초기 데이터 이동
mkdir -p /shared_files
cp -r /docker-entrypoint-initdb.d/shared_files/* /shared_files/

# MariaDB 설정 파일 복사
cp /docker-entrypoint-initdb.d/my.cnf /etc/mysql/mariadb.cnf

# SQL 초기화 스크립트 실행
mysqld_safe --user=mysql &

until mysql -u root -e 'show databases;' >/dev/null 2>&1; do
    sleep 1
done
mysql -u root < /docker-entrypoint-initdb.d/init.sql
mysqladmin shutdown -u root

# MariaDB 서버 재시작
echo "Starting MariaDB server again..."
exec mysqld --user=root