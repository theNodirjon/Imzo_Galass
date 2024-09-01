create database online_shop;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(20),
    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP
);