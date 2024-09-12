-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS file_db;

USE file_db;

-- 사용자 정보 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL
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
((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240812_140000.txt', '/shared_files/20240812/miyeonlim/rep_20240812_140000.txt', '2024-08-12 14:00:00'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240812_141000.txt', '/shared_files/20240812/miyeonlim/rep_20240812_141000.txt', '2024-08-12 14:10:00'),
((SELECT id FROM users WHERE username = 'johnsmith'), 'rep_20240812_120000.txt', '/shared_files/20240812/johnsmith/rep_20240812_120000.txt', '2024-08-12 12:00:00'),

((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240813_080000.pdf', '/shared_files/20240813/miyeonlim/rep_20240813_080000.pdf', '2024-08-13 08:00:00'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240813_090000.xlsx', '/shared_files/20240813/miyeonlim/rep_20240813_090000.xlsx', '2024-08-13 09:00:00'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240813_100000.jpg', '/shared_files/20240813/miyeonlim/rep_20240813_100000.jpg', '2024-08-13 10:00:00'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240813_110000.txt', '/shared_files/20240813/miyeonlim/rep_20240813_110000.txt', '2024-08-13 11:00:00'),
((SELECT id FROM users WHERE username = 'miyeonlim'), 'rep_20240813_120000.txt', '/shared_files/20240813/miyeonlim/rep_20240813_120000.txt', '2024-08-13 12:00:00'),
((SELECT id FROM users WHERE username = 'johnsmith'), 'rep_20240813_120000.txt', '/shared_files/20240813/johnsmith/rep_20240813_120000.txt', '2024-08-13 12:00:00');
