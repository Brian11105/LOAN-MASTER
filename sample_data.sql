USE loan_management_db;


INSERT INTO user (username, email, password_hash, phone_number, id_number, full_name, is_admin) VALUES
('admin', 'admin@loanmaster.co.ke', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', '0712345678', '00000000', 'System Administrator', 1),
('oketch_j', 'james.oketch@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', '0712345678', '12345678', 'James Oketch', 0),
('wambui_m', 'mary.wambui@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', '0723456789', '23456789', 'Mary Wambui', 0),
('odhiambo_p', 'peter.odhiambo@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', '0734567890', '34567890', 'Peter Odhiambo', 0),
('akinyi_s', 'sarah.akinyi@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', '0745678901', '45678901', 'Sarah Akinyi', 0),
('kiprop_d', 'david.kiprop@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', '0756789012', '56789012', 'David Kiprop', 0);


INSERT INTO loan (user_id, loan_amount, interest_rate, loan_period, monthly_installment, total_amount, loan_purpose, status, risk_score, crb_score, crb_npa, crb_history) VALUES
(2, 50000, 10.0, 6, 8750.00, 52500.00, 'Business', 'ACTIVE', 25, 650, 0, 'GOOD'),
(3, 30000, 10.0, 3, 10833.33, 32500.00, 'Education', 'APPROVED', 15, 580, 0, 'GOOD'),
(4, 100000, 10.0, 12, 9166.67, 110000.00, 'Medical', 'PENDING', 45, 520, 1, 'FAIR'),
(5, 75000, 10.0, 6, 13125.00, 78750.00, 'Housing', 'ACTIVE', 30, 600, 0, 'GOOD'),
(6, 25000, 10.0, 3, 9027.78, 27083.33, 'Personal', 'COMPLETED', 10, 680, 0, 'GOOD');

