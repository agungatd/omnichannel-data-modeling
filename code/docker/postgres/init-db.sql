-- Create Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    email VARCHAR(255),
    phone_number VARCHAR(50),
    name VARCHAR(255),
    loyalty_id VARCHAR(50)
);

-- Create Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    source VARCHAR(50),
    created_at TIMESTAMP,
    total_amount DECIMAL(18, 2),
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
);

-- Insert Sample Data
INSERT INTO users (user_id, email, phone_number, name, loyalty_id) VALUES
(1, 'agung@example.com', '+6281234567890', 'Agung', 'LOY-1001'),
(2, 'rianti@example.com', null, 'Rianti', 'LOY-1002');

INSERT INTO orders (order_id, user_id, source, created_at, total_amount) VALUES
(101, 1, 'web', '2024-01-02T10:00:00', 150000),
(102, 1, 'pos', '2024-01-02T15:00:00', 120000);

