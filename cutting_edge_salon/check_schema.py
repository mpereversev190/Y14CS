import sqlite3

conn = sqlite3.connect("salon_database.db")
cur = conn.cursor()

print(cur.execute("PRAGMA table_info(appointments)").fetchall())
