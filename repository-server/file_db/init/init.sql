-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS file_db;

USE file_db;

-- 파일 테이블 생성
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    gitlab_id VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL
);

-- 예시 데이터 삽입
-- 사용자와 파일 데이터 삽입
INSERT IGNORE INTO files (username, gitlab_id, file_name, file_path) VALUES
('miyeonlim', 'gitlab_id_1', 'test1.txt', '/docker-entrypoint-initdb.d/file/test1.txt'),
('miyeonlim', 'gitlab_id_1', 'test2.txt', '/docker-entrypoint-initdb.d/file/test2.txt'),
('johnsmith', 'gitlab_id_2', 'example.txt', '/docker-entrypoint-initdb.d/file/example.txt');