-- database schema
-- run this to reset database: sqlite3 salon.db < schema.sql

-- drop existing tables (for clean rebuild)
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS deletion_log;

-- customers table with soft delete
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone_number TEXT,
    service_type TEXT,
    appointment_date TEXT,
    is_active INTEGER DEFAULT 1,           -- 1 = active, 0 = deleted
    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
    deleted_date TEXT,
    deleted_by INTEGER
);

-- staff table with hashed passwords
CREATE TABLE staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,             -- 1 = admin
    is_active INTEGER DEFAULT 1,             -- 1 = active, 0 = deleted
    last_login TEXT,
    created_date TEXT DEFAULT CURRENT_TIMESTAMP
);

-- appointments for future use
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    staff_id INTEGER,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT,
    service_type TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled',
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

-- audit log for deletions
CREATE TABLE deletion_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    deleted_by INTEGER,
    deleted_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deleted_by) REFERENCES staff(staff_id)
);

-- indexes for faster searching
CREATE INDEX idx_customers_name ON customers(first_name, last_name);
CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_staff_name ON staff(first_name, last_name);

-- insert default admin (password: Admin@123)
-- hash is for 'Admin@123' - generated with bcrypt
INSERT INTO staff (first_name, last_name, email, phone_number, password_hash, is_admin)
VALUES ('Admin', 'User', 'admin@example.com', '+44 1234 567890', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cNpX9Zq6O', 1);

-- sample customers
INSERT INTO customers (first_name, last_name, email, phone_number, service_type, appointment_date)
VALUES 
    ('Sarah', 'Jenkins', 'sarah@email.com', '+44 7123 456789', 'Haircut', '15/03/2024'),
    ('Michael', 'OConnor', 'michael@email.com', '07700 123456', 'Colour', '16/03/2024'),
    ('Emma', 'Williams', 'emma@email.com', '020 7123 4567', 'Consultation', '17/03/2024');