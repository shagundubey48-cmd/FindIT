CREATE DATABASE IF NOT EXISTS finditplus;
USE finditplus;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token_hash VARCHAR(64) NULL,
    verification_token_expires_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
