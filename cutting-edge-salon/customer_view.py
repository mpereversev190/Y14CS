## note to self - run in virtual env . breaks otherwise
# python3 -m venv venv
# source venv/bin/activate
# pip install pillow tkcalendar customtkinter bcrypt python-dotenv
# ctrl+shift+p to venv

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from PIL import Image, ImageTk
import subprocess
import sys
import customtkinter as ctk
from tkcalendar import DateEntry
import csv
from datetime import datetime
import os

# setup for ctk
ctk.set_appearance_mode("system") 
ctk.set_default_color_theme("blue") 

# Get staff info from environment (set during login)
CURRENT_STAFF_ID = os.environ.get('CURRENT_STAFF_ID', '1')
CURRENT_STAFF_NAME = os.environ.get('CURRENT_STAFF_NAME', 'Staff')

# database initialisation 
def init_db():
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    
    # Check if customers table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
    if not cursor.fetchone():
        # Try to run schema file
        try:
            with open('database/schema.sql', 'r') as f:
                cursor.executescript(f.read())
            print("Database schema loaded from file")
        except FileNotFoundError:
            # Fallback - create tables directly
            print("Schema file not found, creating tables directly")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone_number TEXT,
                    service_type TEXT,
                    appointment_date TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
    
    conn.commit()
    conn.close()

init_db()

# validation functions - keeping her regex style
def validate_name(name, field="Name"):
    if not re.match(r"^[A-Za-z\s\-']+$", name.strip()):
        return False, f"{field} should contain letters only"
    return True, ""

def validate_email(email):
    if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        return False, "Invalid email format"
    return True, ""

def validate_phone(phone):
    if not phone:
        return True, ""
    # UK formats
    if re.match(r"^\+44\s?\d{4}\s?\d{6}$", phone) or \
       re.match(r"^07\d{3}\s?\d{6}$", phone) or \
       re.match(r"^0\d{2,4}\s?\d{6}$", phone):
        return True, ""
    return False, "Phone must be UK format (+44 7xxx xxxxxx or 07xxx xxxxxx)"

def validate_date(date_str):
    try:
        day, month, year = map(int, date_str.split('/'))
        datetime(year, month, day)
        return True, ""
    except:
        return False, "Date must be DD/MM/YYYY (e.g., 15/03/2024)"

def validate_all(first, last, email, phone, service, date):
    """Validate all inputs at once"""
    if not service:
        return False, "Please select a service type"
    
    valid, msg = validate_name(first, "First name")
    if not valid: return False, msg
    
    valid, msg = validate_name(last, "Last name")
    if not valid: return False, msg
    
    valid, msg = validate_email(email)
    if not valid: return False, msg
    
    valid, msg = validate_phone(phone)
    if not valid: return False, msg
    
    valid, msg = validate_date(date)
    if not valid: return False, msg
    
    return True, ""

# database functions
def fetch_customers(search_term=""):
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    if search_term:
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone_number, service_type, appointment_date
            FROM customers 
            WHERE is_active = 1 AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone_number LIKE ?)
            ORDER BY appointment_date
        """, ('%' + search_term + '%', '%' + search_term + '%', 
              '%' + search_term + '%', '%' + search_term + '%'))
    else:
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone_number, service_type, appointment_date
            FROM customers 
            WHERE is_active = 1
            ORDER BY appointment_date
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_customer(first_name, last_name, email, phone_number, service_type, appointment_date):
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers
        (first_name, last_name, email, phone_number, service_type, appointment_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (first_name, last_name, email, phone_number, service_type, appointment_date))
    conn.commit()
    conn.close()
    refresh_tree()

def update_customer(customer_id, first_name, last_name, email, phone_number, service_type, appointment_date):
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET first_name=?, last_name=?, email=?, phone_number=?, service_type=?, appointment_date=?
        WHERE id=?
    """, (first_name, last_name, email, phone_number, service_type, appointment_date, customer_id))
    conn.commit()
    conn.close()
    refresh_tree()

def delete_customer():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a customer to delete.")
        return
    item = tree.item(selected[0])
    customer_id = item["values"][0]
    name = f"{item['values'][1]} {item['values'][2]}"
    
    confirm = messagebox.askyesno("Confirm Delete", 
                                  f"Delete {name}? (This hides them - can restore later)")
    if not confirm:
        return
    
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    # soft delete
    cursor.execute("UPDATE customers SET is_active = 0 WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()
    refresh_tree()
    messagebox.showinfo("Deleted", f"{name} has been hidden.")

def export_customers():
    """Export to CSV"""
    customers = fetch_customers()
    if not customers:
        messagebox.showwarning("No Data", "No customers to export")
        return
    
    if not os.path.exists('exports'):
        os.makedirs('exports')
    
    filename = f"exports/customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Service', 'Date'])
            writer.writerows(customers)
        messagebox.showinfo("Success", f"Exported to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Export failed: {e}")

# back button function
def back_to_main_menu():
    subprocess.Popen(["python3", "main_menu.py"])
    root.destroy()

# refresh tree
def refresh_tree(search_term=""):
    for item in tree.get_children():
        tree.delete(item)
    for row in fetch_customers(search_term):
        tree.insert("", tk.END, values=row)
    count_label.configure(text=f"Records: {len(fetch_customers(search_term))}")

# setup gui
root = ctk.CTk()
root.title("Customer Manager")
root.geometry("1100x650")

# configure grid
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(2, weight=1)

# header frame
header_frame = ctk.CTkFrame(root)
header_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
header_frame.grid_columnconfigure(1, weight=1)

# logo
try:
    img = Image.open("logo.png")
    img = img.resize((80, 80))
    logo_img = ImageTk.PhotoImage(img)
    logo_label = tk.Label(header_frame, image=logo_img)
    logo_label.image = logo_img
    logo_label.grid(row=0, column=0, padx=10)
except:
    ctk.CTkLabel(header_frame, text="🏢", font=("Arial", 40)).grid(row=0, column=0, padx=10)

# title
ctk.CTkLabel(header_frame, text="Customer Management", 
             font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=1, padx=10, sticky="w")

# back button
ctk.CTkButton(header_frame, text="← Back to Menu", command=back_to_main_menu,
              width=120).grid(row=0, column=2, padx=10)

# search frame
search_frame = ctk.CTkFrame(root)
search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
search_frame.grid_columnconfigure(1, weight=1)

ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=5)
search_entry = ctk.CTkEntry(search_frame, placeholder_text="Name, email, or phone...", width=300)
search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

def do_search():
    refresh_tree(search_entry.get().strip())

ctk.CTkButton(search_frame, text="Search", command=do_search, width=80).grid(row=0, column=2, padx=5)
ctk.CTkButton(search_frame, text="Clear", command=lambda: [search_entry.delete(0,'end'), refresh_tree()], 
              width=80, fg_color="gray").grid(row=0, column=3, padx=5)

# action buttons
ctk.CTkButton(search_frame, text="➕ Add", command=lambda: open_add_window(), 
              width=80, fg_color="#2b8c4a").grid(row=0, column=4, padx=5)
ctk.CTkButton(search_frame, text="✏️ Edit", command=lambda: open_edit_window(), 
              width=80).grid(row=0, column=5, padx=5)
ctk.CTkButton(search_frame, text="🗑️ Delete", command=delete_customer, 
              width=80, fg_color="#c0392b").grid(row=0, column=6, padx=5)
ctk.CTkButton(search_frame, text="📤 Export", command=export_customers, 
              width=80).grid(row=0, column=7, padx=5)

# treeview
tree_frame = ctk.CTkFrame(root)
tree_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
tree_frame.grid_columnconfigure(0, weight=1)
tree_frame.grid_rowconfigure(0, weight=1)

columns = ("ID", "First Name", "Last Name", "Email", "Phone", "Service", "Date")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120 if col != "Email" else 180)

vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)

tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

# bind double-click to edit
tree.bind('<Double-1>', lambda e: open_edit_window())

# status bar
status_frame = ctk.CTkFrame(root)
status_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
status_frame.grid_columnconfigure(1, weight=1)

count_label = ctk.CTkLabel(status_frame, text="Records: 0")
count_label.grid(row=0, column=0, padx=10)

ctk.CTkLabel(status_frame, text=f"Staff: {CURRENT_STAFF_NAME}").grid(row=0, column=2, padx=10)

refresh_tree()

# add window function
def open_add_window():
    add_window = ctk.CTkToplevel(root)
    add_window.title("Add New Customer")
    add_window.geometry("450x420")
    add_window.resizable(False,False)
    add_window.transient(root)
    add_window.grab_set()
    
    # form fields
    row = 0
    
    ctk.CTkLabel(add_window, text="First Name:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    first_entry = ctk.CTkEntry(add_window, width=250)
    first_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(add_window, text="Last Name:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    last_entry = ctk.CTkEntry(add_window, width=250)
    last_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(add_window, text="Email:").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    email_entry = ctk.CTkEntry(add_window, width=250, placeholder_text="optional")
    email_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(add_window, text="Phone:").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    phone_entry = ctk.CTkEntry(add_window, width=250, placeholder_text="+44 7123 456789")
    phone_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(add_window, text="Service:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    service_var = ctk.StringVar(value="Haircut")
    service_dropdown = ttk.Combobox(add_window, textvariable=service_var,
                                    values=["Haircut", "Wash & Blow Dry", "Colour", 
                                           "Highlights", "Toner", "Consultation"],
                                    state="readonly", width=30)
    service_dropdown.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(add_window, text="Date (DD/MM/YYYY):*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    date_picker = DateEntry(add_window, width=12, date_pattern='dd/mm/yyyy',
                           background='darkblue', foreground='white', borderwidth=2)
    date_picker.grid(row=row, column=1, padx=10, pady=8, sticky="w")
    row += 1
    
    ctk.CTkLabel(add_window, text="* Required fields", font=("Arial", 10, "italic"),
                text_color="gray").grid(row=row, column=0, columnspan=2, pady=5)
    row += 1
    
    def submit():
        valid, msg = validate_all(
            first_entry.get().strip(),
            last_entry.get().strip(),
            email_entry.get().strip(),
            phone_entry.get().strip(),
            service_var.get(),
            date_picker.get()
        )
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return
        
        add_customer(
            first_entry.get().strip(),
            last_entry.get().strip(),
            email_entry.get().strip(),
            phone_entry.get().strip(),
            service_var.get(),
            date_picker.get()
        )
        messagebox.showinfo("Success", "Customer added successfully!")
        add_window.destroy()
    
    # buttons
    btn_frame = ctk.CTkFrame(add_window)
    btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
    
    ctk.CTkButton(btn_frame, text="Add Customer", command=submit, 
                  fg_color="#2b8c4a").pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Cancel", command=add_window.destroy).pack(side="left", padx=5)
    
    # bind enter key
    add_window.bind('<Return>', lambda e: submit())

# edit window function
def open_edit_window():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a customer to edit")
        return
    
    item = tree.item(selected[0])
    customer_id, first_name, last_name, email, phone_number, service_type, appointment_date = item["values"]
    
    edit_window = ctk.CTkToplevel(root)
    edit_window.title(f"Edit Customer")
    edit_window.geometry("450x420")
    edit_window.resizable(False,False)
    edit_window.transient(root)
    edit_window.grab_set()
    
    # form fields with pre-filled data
    row = 0
    
    ctk.CTkLabel(edit_window, text="First Name:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    first_entry = ctk.CTkEntry(edit_window, width=250)
    first_entry.insert(0, first_name)
    first_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(edit_window, text="Last Name:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    last_entry = ctk.CTkEntry(edit_window, width=250)
    last_entry.insert(0, last_name)
    last_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(edit_window, text="Email:").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    email_entry = ctk.CTkEntry(edit_window, width=250)
    email_entry.insert(0, email)
    email_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(edit_window, text="Phone:").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    phone_entry = ctk.CTkEntry(edit_window, width=250)
    phone_entry.insert(0, phone_number)
    phone_entry.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(edit_window, text="Service:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    service_var = ctk.StringVar(value=service_type)
    service_dropdown = ttk.Combobox(edit_window, textvariable=service_var,
                                    values=["Haircut", "Wash & Blow Dry", "Colour", 
                                           "Highlights", "Toner", "Consultation"],
                                    state="readonly", width=30)
    service_dropdown.grid(row=row, column=1, padx=10, pady=8)
    row += 1
    
    ctk.CTkLabel(edit_window, text="Date (DD/MM/YYYY):*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
    date_picker = DateEntry(edit_window, width=12, date_pattern='dd/mm/yyyy',
                           background='darkblue', foreground='white', borderwidth=2)
    try:
        day, month, year = map(int, appointment_date.split('/'))
        date_picker.set_date(datetime(year, month, day))
    except:
        pass
    date_picker.grid(row=row, column=1, padx=10, pady=8, sticky="w")
    row += 1
    
    def save():
        valid, msg = validate_all(
            first_entry.get().strip(),
            last_entry.get().strip(),
            email_entry.get().strip(),
            phone_entry.get().strip(),
            service_var.get(),
            date_picker.get()
        )
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return
        
        update_customer(
            customer_id,
            first_entry.get().strip(),
            last_entry.get().strip(),
            email_entry.get().strip(),
            phone_entry.get().strip(),
            service_var.get(),
            date_picker.get()
        )
        messagebox.showinfo("Success", "Customer updated successfully!")
        edit_window.destroy()
    
    # buttons
    btn_frame = ctk.CTkFrame(edit_window)
    btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
    
    ctk.CTkButton(btn_frame, text="Save Changes", command=save, 
                  fg_color="#2b8c4a").pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Cancel", command=edit_window.destroy).pack(side="left", padx=5)

# run
if __name__ == "__main__":
    root.mainloop()