CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

CREATE TABLE IF NOT EXISTS product_price (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    product_id VARCHAR(10),
    own_price DECIMAL(10,2),
    competitor_price DECIMAL(10,2),
    cost DECIMAL(10,2),
    stock INT
);
