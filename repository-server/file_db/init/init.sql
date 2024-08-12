-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS file_db;

USE file_db;

-- 사용자 정보 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
);

-- 파일 테이블 생성
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 예시 데이터 삽입
INSERT IGNORE INTO users (username) VALUES
('miyeonlim'),
('johnsmith');

-- 사용자 ID를 서브쿼리로 조회하여 파일 데이터 삽입
INSERT INTO files (user_id, file_name, file_path, created_at) VALUES
((SELECT id FROM users WHERE username = 'miyeonlim'), 'test1.txt', '/20240812/miyeonlim/test1.txt', '2024-08-12 10:00:00'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'test2.txt', '/20240812/miyeonlim/test2.txt', '2024-08-12 11:00:00'),
((SELECT id FROM users WHERE username = 'johnsmith'), 'example.txt', '/20240812/johnsmith/example.txt', '2024-08-12 12:00:00');
