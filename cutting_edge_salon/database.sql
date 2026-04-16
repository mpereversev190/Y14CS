

-- 1. users table
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
    "role" TEXT NOT NULL DEFAULT 'customer',
    "status" TEXT NOT NULL DEFAULT 'active'
);

-- 2. services table
CREATE TABLE IF NOT EXISTS "services" (
    "service_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "service_name" TEXT NOT NULL,
    "description" TEXT,
    "price" REAL NOT NULL,
    "duration_minutes" INTEGER NOT NULL DEFAULT 30
);

-- prevent duplicate service names
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_service_name
ON services(service_name);

-- 3. appointments table
CREATE TABLE IF NOT EXISTS "appointments" (
    "appointment_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "customer_id" INTEGER NOT NULL,
    "stylist_id" INTEGER NOT NULL,
    "service_id" INTEGER NOT NULL,
    "appointment_datetime" DATETIME NOT NULL,
    "notes" TEXT,
    "status" TEXT NOT NULL DEFAULT 'booked',
    
    FOREIGN KEY("customer_id") REFERENCES "users"("user_id"),
    FOREIGN KEY("stylist_id") REFERENCES "users"("user_id"),
    FOREIGN KEY("service_id") REFERENCES "services"("service_id")
);

-- 4. payments table
CREATE TABLE IF NOT EXISTS "payments" (
    "payment_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "appointment_id" INTEGER NOT NULL,
    "amount" REAL NOT NULL,
    "payment_date" DATETIME DEFAULT CURRENT_TIMESTAMP,
    "payment_method" TEXT,
    "status" TEXT NOT NULL DEFAULT 'pending',
    
    FOREIGN KEY("appointment_id") REFERENCES "appointments"("appointment_id")
);

-- data seed for testing

INSERT OR IGNORE INTO users (username, password, email, role, first_name, last_name) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin@cuttingedge.com', 'admin', 'Salon', 'Manager');
