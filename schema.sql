CREATE DATABASE IF NOT EXISTS deepfake_db CHARACTER SET utf8mb4;
USE deepfake_db;

-- 사용자 원본 이미지 테이블
CREATE TABLE IF NOT EXISTS user_images (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  original_image LONGBLOB NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 탐지 결과 테이블
CREATE TABLE IF NOT EXISTS detection_results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  filename VARCHAR(255),
  psnr FLOAT NULL,
  ssim FLOAT NULL,
  confidence FLOAT NULL,
  status VARCHAR(50),          -- "real", "fake", "photoshop" 등
  source VARCHAR(50),          -- "DB", "FF++" 등
  edit_type VARCHAR(50) DEFAULT 'normal',
  visualization VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
