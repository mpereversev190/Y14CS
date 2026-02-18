import hashlib
import sqlite3
import datetime
from enum import Enum
from typing import Optional

# --- ADAPTERS AND CONVERTERS ---
def adapt_date_iso(val): return val.isoformat()
def adapt_datetime_iso(val): return val.replace(tzinfo=None).isoformat()
sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)

def convert_date(val): return datetime.date.fromisoformat(val.decode())
def convert_datetime(val): return datetime.datetime.fromisoformat(val.decode())
sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)

# ======================
# ENUMS
# ======================
class UserRole(Enum):
    customer = "customer"
    staff = "staff"
    stylist = "stylist"
    admin = "admin"

class UserStatus(Enum):
    active = "active"
    inactive = "inactive"

class AppointmentStatus(Enum):
    booked = "booked"
    completed = "completed"
    cancelled = "cancelled"

# ======================
# DATA MODELS
# ======================
class User:
    # Matches your teaching structure: Includes joined_date and last_login
    def __init__(self, user_id, username, password, email, birth_date,
                 joined_date, last_login, role: UserRole, status: UserStatus,
                 first_name=None, last_name=None, phone_number=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.birth_date = birth_date
        self.joined_date = joined_date
        self.last_login = last_login
        self.role = role
        self.status = status
        # Salon specific fields
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number

# ======================
# DATABASE CLASS
# ======================
class Database:
    def __init__(self):
        # 1. Setup the connection first
        self.conn = sqlite3.connect(
            "salon_database.db",
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False
        )
        # 2. Create the cursor second
        self.cur = self.conn.cursor()

        # 3. NOW call the initialization methods
        self.init_db()

    def init_db(self):
        try:
            with open("database.sql", "r") as file:
                script = file.read()
                self.cur.executescript(script)
            
            # --- UPDATED FORCE SYNC ---
            # We add dummy values for email and names to satisfy the database constraints
            admin_pw = self.hash_password("admin123")
            self.cur.execute("""
                INSERT OR REPLACE INTO users (user_id, username, password, email, role, status, first_name, last_name)
                VALUES (1, 'admin', ?, 'admin@salon.com', 'admin', 'active', 'Salon', 'Manager')
            """, (admin_pw,))
            
            self.conn.commit()
            print(f"DEBUG: Database initialized and admin synced with email.")
        except Exception as e:
            print(f"DEBUG: SQL Error: {e}")

    # -------------------------
    # Password hashing
    # -------------------------
    def hash_password(self, password: str):
        return hashlib.sha256(password.encode()).hexdigest()

    # -------------------------
    # USERS & AUTHENTICATION
    # -------------------------
    def login(self, username, password):
        hashed_input = self.hash_password(password)
        print(f"DEBUG: Attempting login for: {username}")
        print(f"DEBUG: Input Password Hash: {hashed_input}")

        q = "SELECT password FROM users WHERE username=?"
        self.cur.execute(q, (username,))
        result = self.cur.fetchone()
        
        if result:
            print(f"DEBUG: DB Stored Hash:    {result[0]}")
            if result[0] == hashed_input:
                # If they match, fetch the full user
                q_full = """SELECT user_id, username, password, email, birth_date, 
                                  joined_date, last_login, role, status 
                           FROM users WHERE username=?"""
                self.cur.execute(q_full, (username,))
                row = self.cur.fetchone()
                return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                            UserRole(row[7]), UserStatus(row[8]))
        
        print("DEBUG: Mismatch or User not found.")
        return None

    def fetch_all_staff(self, search_term=""):
        if search_term:
            q = """SELECT user_id, first_name, last_name, email, phone_number 
                   FROM users WHERE role != 'customer' 
                   AND (first_name LIKE ? OR last_name LIKE ?)"""
            self.cur.execute(q, ('%' + search_term + '%', '%' + search_term + '%'))
        else:
            q = "SELECT user_id, first_name, last_name, email, phone_number FROM users WHERE role != 'customer'"
            self.cur.execute(q)
        return self.cur.fetchall()

    def fetch_all_customers(self, search_term=""):
        if search_term:
            q = """SELECT user_id, first_name, last_name, email, phone_number 
                   FROM users WHERE role = 'customer' 
                   AND (first_name LIKE ? OR last_name LIKE ?)"""
            self.cur.execute(q, ('%' + search_term + '%', '%' + search_term + '%'))
        else:
            q = "SELECT user_id, first_name, last_name, email, phone_number FROM users WHERE role = 'customer'"
            self.cur.execute(q)
        return self.cur.fetchall()

    def delete_user(self, user_id):
        self.cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.conn.commit()

# Instantiate the DB object exactly as you taught
db = Database()