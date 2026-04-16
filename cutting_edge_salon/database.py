import hashlib
import sqlite3
import datetime
from enum import Enum
from typing import Optional

# --- adapters ---
def adapt_date_iso(val):
    return val.isoformat()

def adapt_datetime_iso(val):
    return val.replace(tzinfo=None).isoformat()

sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)


# --- Converters (SAFE) ---
def convert_date(val):
    if val is None:
        return None
    try:
        return datetime.date.fromisoformat(val.decode())
    except Exception:
        # return none instead of crashing if the DB contains invalid data
        return None


def convert_datetime(val):
    if val is None:
        return None

    s = val.decode()

    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:
        return None



sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)

# enums
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

# data models
class User:
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
        #  specific fields
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number

def get_role_by_id(self, user_id):
    self.cur.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = self.cur.fetchone()
    return row[0] if row else "Unknown"


#database class
class Database:
    def __init__(self):
        # set up the connection first
        self.conn = sqlite3.connect(
            "salon_database.db",
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False
        )
        # create the cursor second
        self.cur = self.conn.cursor()

        # call the initialization methods
        self.init_db()

    def init_db(self):
        try:
            with open("database.sql", "r") as file:
                script = file.read()
                self.cur.executescript(script)
            
            # updated force sync
            #add dummy values for email and names to satisfy the database constraints
            admin_pw = self.hash_password("admin123")
            self.cur.execute("""
                INSERT OR REPLACE INTO users (user_id, username, password, email, role, status, first_name, last_name)
                VALUES (1, 'admin', ?, 'admin@salon.com', 'admin', 'active', 'Salon', 'Manager')
            """, (admin_pw,))
            
            self.conn.commit()
            print(f"DEBUG: Database initialized and admin synced with email.")
        except Exception as e:
            print(f"DEBUG: SQL Error: {e}")

    # password hashing
    def hash_password(self, password: str):
        return hashlib.sha256(password.encode()).hexdigest()

    # users+authentication
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
                # if they match, fetch the full user
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

    def fetch_customers(self):
        q = """
            SELECT user_id, first_name || ' ' || last_name AS full_name
            FROM users
            WHERE role = 'customer'
            ORDER BY first_name
        """
        self.cur.execute(q)
        return self.cur.fetchall()
    
    def fetch_appointments_with_prices(self):
        q = """
        SELECT 
            a.appointment_id,
            a.appointment_datetime,
            u.first_name || ' ' || u.last_name AS customer_name,
            s.service_name,
            s.price
        FROM appointments a
        JOIN users u ON a.customer_id = u.user_id
        JOIN services s ON a.service_id = s.service_id
        ORDER BY a.appointment_datetime DESC
    """
        self.cur.execute(q)
        return self.cur.fetchall()

    
    def fetch_all_payments(self, search_term=""):
        if search_term:
            q = """
                SELECT 
                    p.payment_id,
                    p.appointment_id,
                    u.first_name || ' ' || u.last_name AS customer_name,
                    p.amount,
                    p.payment_date,
                    p.payment_method,
                    p.status
                FROM payments p
                JOIN appointments a ON p.appointment_id = a.appointment_id
                JOIN users u ON a.customer_id = u.user_id
                WHERE u.first_name LIKE ? OR u.last_name LIKE ?
                ORDER BY p.payment_date DESC
            """
            self.cur.execute(q, ('%' + search_term + '%', '%' + search_term + '%'))
        else:
            q = """
                SELECT 
                    p.payment_id,
                    p.appointment_id,
                    u.first_name || ' ' || u.last_name AS customer_name,
                    p.amount,
                    p.payment_date,
                    p.payment_method,
                    p.status
                FROM payments p
                JOIN appointments a ON p.appointment_id = a.appointment_id
                JOIN users u ON a.customer_id = u.user_id
                ORDER BY p.payment_date DESC
            """
            self.cur.execute(q)

        return self.cur.fetchall()


    def fetch_stylists(self):
        q = """
            SELECT user_id, first_name || ' ' || last_name AS full_name
            FROM users
            WHERE role IN ('staff', 'stylist')
            ORDER BY first_name
        """
        self.cur.execute(q)
        return self.cur.fetchall()


    def fetch_services(self):
        q = """
            SELECT service_id, service_name
            FROM services
            ORDER BY service_name
        """
        self.cur.execute(q)
        return self.cur.fetchall()

    def fetch_all_appointments(self, search_term=""):
        if search_term:
            q = """
                SELECT 
                    a.appointment_id,
                    a.appointment_datetime,
                    a.notes,
                    a.status,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    s.first_name || ' ' || s.last_name AS stylist_name,
                    sv.service_name
                FROM appointments a
                JOIN users c ON a.customer_id = c.user_id
                JOIN users s ON a.stylist_id = s.user_id
                JOIN services sv ON a.service_id = sv.service_id
                WHERE c.first_name LIKE ? OR c.last_name LIKE ?
                ORDER BY a.appointment_datetime
            """
            self.cur.execute(q, ('%' + search_term + '%', '%' + search_term + '%'))
        else:
            q = """
                SELECT 
                    a.appointment_id,
                    a.appointment_datetime,
                    a.notes,
                    a.status,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    s.first_name || ' ' || s.last_name AS stylist_name,
                    sv.service_name
                FROM appointments a
                JOIN users c ON a.customer_id = c.user_id
                JOIN users s ON a.stylist_id = s.user_id
                JOIN services sv ON a.service_id = sv.service_id
                ORDER BY a.appointment_datetime
            """
            self.cur.execute(q)

        return self.cur.fetchall()

    def delete_appointment(self, appointment_id):
        self.cur.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
        self.conn.commit()


    def insert_payment(self, appointment_id, amount, method, status,
                    card_last4=None, card_expiry=None, card_holder=None):

        q = """
            INSERT INTO payments (
                appointment_id, amount, payment_method, status,
                card_last4, card_expiry, card_holder
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.cur.execute(q, (
            appointment_id, amount, method, status,
            card_last4, card_expiry, card_holder
        ))
        self.conn.commit()

    def update_payment(self, payment_id, method, status,
                    card_last4=None, card_expiry=None, card_holder=None):

        q = """
            UPDATE payments
            SET payment_method=?, status=?, card_last4=?, card_expiry=?, card_holder=?
            WHERE payment_id=?
        """

        self.cur.execute(q, (
            method, status, card_last4, card_expiry, card_holder, payment_id
        ))
        self.conn.commit()


    def delete_payment(self, payment_id):
        self.cur.execute("DELETE FROM payments WHERE payment_id=?", (payment_id,))
        self.conn.commit()






db = Database()