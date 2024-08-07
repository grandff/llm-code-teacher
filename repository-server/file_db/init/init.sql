-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS file_db;

USE file_db;

-- 사용자 정보 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    gitlab_id VARCHAR(255) NOT NULL
);

-- 파일 테이블 생성
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 예시 데이터 삽입
INSERT IGNORE INTO users (username, gitlab_id) VALUES
('miyeonlim', 'gitlab_id_1'),
('johnsmith', 'gitlab_id_2');

-- 사용자 ID를 서브쿼리로 조회하여 파일 데이터 삽입
INSERT INTO files (user_id, file_name, file_path) VALUES
((SELECT id FROM users WHERE username = 'miyeonlim'), 'test1.txt', '/miyeonlim/gitlab_id_1/test1.txt'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'test2.txt', '/miyeonlim/gitlab_id_1/test2.txt'),
((SELECT id FROM users WHERE username = 'johnsmith'), 'example.txt', '/johnsmith/gitlab_id_2/example.txt');