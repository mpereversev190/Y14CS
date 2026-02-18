-- ======================================================
-- CUTTING EDGE HAIR SALON - DATABASE SCHEMA
-- ======================================================

-- 1. USERS TABLE
-- Consolidates members, staff, and admins into one relational table.
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "email" TEXT NOT NULL UNIQUE,
    "first_name" TEXT,
    "last_name" TEXT,
    "phone_number" TEXT,
    "birth_date" DATE,
    "joined_date" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "last_login" DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Roles: 'customer', 'staff' (Receptionist), 'stylist' (Junior/Senior), 'admin'
    "role" TEXT NOT NULL DEFAULT 'customer',
    -- Status: 'active', 'inactive'
    "status" TEXT NOT NULL DEFAULT 'active'
);

-- 2. SERVICES TABLE
-- Defines what the salon offers (replaces 'Gym Classes')
CREATE TABLE IF NOT EXISTS "services" (
    "service_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "service_name" TEXT NOT NULL, -- e.g., 'Restyle & Finish', 'Balayage'
    "description" TEXT,
    "price" REAL NOT NULL,
    "duration_minutes" INTEGER NOT NULL DEFAULT 30
);

-- 3. APPOINTMENTS TABLE
-- Links a customer, a stylist, and a specific service (replaces 'Bookings')
CREATE TABLE IF NOT EXISTS "appointments" (
    "appointment_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "customer_id" INTEGER NOT NULL,
    "stylist_id" INTEGER NOT NULL,
    "service_id" INTEGER NOT NULL,
    "appointment_datetime" DATETIME NOT NULL,
    "notes" TEXT,
    "status" TEXT NOT NULL DEFAULT 'booked', -- 'booked', 'completed', 'cancelled', 'no-show'
    
    FOREIGN KEY("customer_id") REFERENCES "users"("user_id"),
    FOREIGN KEY("stylist_id") REFERENCES "users"("user_id"),
    FOREIGN KEY("service_id") REFERENCES "services"("service_id")
);

-- 4. PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS "payments" (
    "payment_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "appointment_id" INTEGER NOT NULL,
    "amount" REAL NOT NULL,
    "payment_date" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "payment_method" TEXT, -- 'card', 'cash', 'gift_voucher'
    "status" TEXT NOT NULL DEFAULT 'pending',
    
    FOREIGN KEY("appointment_id") REFERENCES "appointments"("appointment_id")
);

-- ======================================================
-- INITIAL DATA SEEDING (For Testing)
-- ======================================================

-- Default Admin (Password: admin123)
-- In production, the password should be hashed via database.py
INSERT OR IGNORE INTO users (username, password, email, role, first_name, last_name) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin@cuttingedge.com', 'admin', 'Salon', 'Manager');



-- Sample Services
INSERT OR IGNORE INTO services (service_name, price, duration_minutes) VALUES 
('Gents Cut', 25.00, 30),
('Ladies Restyle', 45.00, 60),
('Full Head Colour', 85.00, 120);