-- Create database
CREATE DATABASE IF NOT EXISTS loan_management_db;
USE loan_management_db;


CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    id_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);


CREATE TABLE IF NOT EXISTS loan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    loan_amount FLOAT NOT NULL,
    interest_rate FLOAT DEFAULT 10.0,
    loan_period INT NOT NULL,
    monthly_installment FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    loan_purpose VARCHAR(200),
    status VARCHAR(20) DEFAULT 'PENDING',
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    approval_date DATETIME,
    due_date DATETIME,
    risk_score INT DEFAULT 0,
    crb_score INT DEFAULT 500,
    crb_npa INT DEFAULT 0,
    crb_history VARCHAR(20) DEFAULT 'GOOD',
    crb_recommendation VARCHAR(200),
    risk_with_crb INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE IF NOT EXISTS payment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    amount FLOAT NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    payment_method VARCHAR(20) DEFAULT 'MANUAL',
    receipt_number VARCHAR(50),
    mpesa_transaction_id VARCHAR(50) UNIQUE,
    mpesa_phone_number VARCHAR(20),
    FOREIGN KEY (loan_id) REFERENCES loan(id)
);


CREATE TABLE IF NOT EXISTS transaction_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    transaction_type VARCHAR(50) NOT NULL,
    amount FLOAT,
    description VARCHAR(200),
    reference VARCHAR(50),
    status VARCHAR(20),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    encrypted_data TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE IF NOT EXISTS crb_simulation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    national_id VARCHAR(20) NOT NULL,
    full_name VARCHAR(100),
    phone_number VARCHAR(20),
    credit_score INT DEFAULT 500,
    credit_rating VARCHAR(20) DEFAULT 'FAIR',
    npa_count INT DEFAULT 0,
    payment_history VARCHAR(20) DEFAULT 'GOOD',
    default_history BOOLEAN DEFAULT FALSE,
    simulated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE IF NOT EXISTS crb_simulation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    loan_id INT,
    credit_score INT,
    risk_level VARCHAR(20),
    is_simulated BOOLEAN DEFAULT TRUE,
    checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);