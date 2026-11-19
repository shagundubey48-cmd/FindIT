-- Run order for a fresh database:
--   1. schema.sql         (users, items)
--   2. claims.sql
--   3. handovers.sql
--   4. feedback.sql
--   5. notifications.sql
--   6. remaining_features.sql
-- The *_migration.sql files are ONLY for databases created before those
-- columns existed. Do not run them on a fresh database.
-- (Alternatively run `python init_db.py` to create everything from the models.)

CREATE DATABASE IF NOT EXISTS finditplus;
USE finditplus;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token_hash VARCHAR(64) NULL,
    verification_token_expires_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    campus VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    item_type VARCHAR(20) NOT NULL DEFAULT 'lost',
    item_date DATE NOT NULL,
    image_url VARCHAR(500) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    admin_remarks TEXT NULL,
    moderated_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_item_user
        FOREIGN KEY (user_id) REFERENCES users(id)
);
