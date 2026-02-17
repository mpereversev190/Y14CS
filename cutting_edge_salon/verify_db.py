import sqlite3
import hashlib

db_file = "salon_database.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()

print("--- Database Verification ---")
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print(f"Tables found: {tables}")

    cur.execute("SELECT username, password, role FROM users")
    users = cur.fetchall()
    print(f"Users found: {len(users)}")
    
    for u in users:
        print(f"  > User: {u[0]} | Role: {u[2]}")
        # Verify if the hash matches admin123
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        if u[1] == admin_hash:
            print("    ✅ Hash matches 'admin123'")
        else:
            print(f"    ❌ Hash mismatch! DB has: {u[1][:10]}...")

except Exception as e:
    print(f"❌ Error: {e}")

conn.close()