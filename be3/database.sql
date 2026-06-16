CREATE DATABASE IF NOT EXISTS `recognition-kp` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `recognition-kp`;

CREATE TABLE IF NOT EXISTS admins (
    id         INT          NOT NULL AUTO_INCREMENT,
    username   VARCHAR(100) NOT NULL,
    password   VARCHAR(255) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    role       VARCHAR(50)  NOT NULL DEFAULT 'admin',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS users (
    id         INT          NOT NULL AUTO_INCREMENT,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    phone      VARCHAR(20),
    embeddings TEXT,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id         INT          NOT NULL AUTO_INCREMENT,
    user_id    INT          NOT NULL,
    check_type VARCHAR(20)  NOT NULL COMMENT 'check_in atau check_out',
    confidence FLOAT        NOT NULL,
    timestamp  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
