CREATE DATABASE IF NOT EXISTS web_site;
USE web_site;

CREATE TABLE IF NOT EXISTS users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'visitor') DEFAULT 'visitor'
)

CREATE TABLE IF NOT EXISTS recipes (
    id_recipe INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    image_path VARCHAR(255),
    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS favorites (
    id_user INT,
    id_recipe INT,
    PRIMARY KEY (id_user, id_recipe),
    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_recipe) REFERENCES recipes(id_recipe) ON DELETE CASCADE
)