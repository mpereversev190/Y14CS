## note to self - run in virtual env . breaks otherwise
# python3 -m venv venv
# source venv/bin/activate
# pip install pillow tkcalendar customtkinter
# ctrl+shift+p to venv

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from PIL import Image, ImageTk
import subprocess
import sys
import customtkinter as ctk

# setup for ctk
ctk.set_appearance_mode("system") 
ctk.set_default_color_theme("blue") 

# database initialisation
def init_db():
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone_number TEXT,
            service_type TEXT,
            appointment_date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# validation function
def validate_inputs(first_name, last_name, email, phone, appointment_date):
    if not re.match(r"^[A-Za-z]+$", first_name):
        return False, "First name should contain letters only."
    if not re.match(r"^[A-Za-z]+$", last_name):
        return False, "Last name should contain letters only."
    if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        return False, "Invalid email format."
    if phone and not re.match(r"^(?:\+44\s?7\d{3}\s?\d{6}|07\d{3}\s?\d{6})$", phone):
        return False, "Phone number must be UK format (+44 7xxx xxxxxx or 07xxx xxxxxx)."
    if not re.match(r"^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/[0-9]{4}$", appointment_date):
        return False, "Date must be in DD/MM/YYYY format."
    return True, ""

# database functions
def fetch_customers(search_term=""):
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    if search_term:
        cursor.execute("""
            SELECT * FROM customers 
            WHERE first_name LIKE ? OR last_name LIKE ?
        """, ('%' + search_term + '%', '%' + search_term + '%'))
    else:
        cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_customer(first_name, last_name, email, phone_number, service_type, appointment_date):
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers
        (first_name, last_name, email, phone_number, service_type, appointment_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, email, phone_number, service_type, appointment_date))
    conn.commit()
    conn.close()
    refresh_tree()

def update_customer(customer_id, first_name, last_name, email, phone_number, service_type, appointment_date):
    conn = sqlite3.connect("customers.db")
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
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?")
    if not confirm:
        return
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()
    refresh_tree()
    messagebox.showinfo("Deleted", f"{name} has been deleted.")

# back button function
def back_to_main_menu():
    subprocess.Popen(["python3", "main_menu.py"])
    root.destroy()

# setup for gui
root = tk.Tk()
root.title("Customer Manager")
root.geometry("1000x600")
root.resizable(False,False)

header_frame = tk.Frame(root)
header_frame.pack(pady=10)

# logo
try:
    img = Image.open("logo.png")
    img = img.resize((150, 120))
    logo_img = ImageTk.PhotoImage(img)
    logo_label = tk.Label(header_frame, image=logo_img)
    logo_label.image = logo_img
    logo_label.pack()
except FileNotFoundError:
    tk.Label(header_frame, text="Logo not found (logo.png)").pack()

# back button (redirect to main menu)
ctk.CTkButton(
    header_frame,
    text="Back to Main Menu",
    command=back_to_main_menu
).pack(pady=10)

# treeview
columns = ("ID", "First Name", "Last Name", "Email Address", "Phone Number", "Service Type", "Appointment Date")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140)
tree.pack(fill=tk.BOTH, expand=True, pady=10)

def refresh_tree(search_term=""):
    for item in tree.get_children():
        tree.delete(item)
    for row in fetch_customers(search_term):
        tree.insert("", tk.END, values=row)

refresh_tree()

# search text input 
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Search (First or Last Name):").grid(row=0, column=0)
search_entry = tk.Entry(frame)
search_entry.grid(row=0, column=1)

def search_action():
    refresh_tree(search_entry.get().strip())

# add window 
def open_add_window():
    add_window = tk.Toplevel(root)
    add_window.title("Add New Customer")
    add_window.geometry("450x250")
    add_window.resizable(False,False)

    tk.Label(add_window, text="First Name:").grid(row=0, column=0, pady=5, sticky="e")
    first_name_entry = tk.Entry(add_window)
    first_name_entry.grid(row=0, column=1)

    tk.Label(add_window, text="Last Name:").grid(row=1, column=0, pady=5, sticky="e")
    last_name_entry = tk.Entry(add_window)
    last_name_entry.grid(row=1, column=1)

    tk.Label(add_window, text="Email Address:").grid(row=2, column=0, pady=5, sticky="e")
    email_entry = tk.Entry(add_window)
    email_entry.grid(row=2, column=1)

    tk.Label(add_window, text="Phone Number:").grid(row=3, column=0, pady=5, sticky="e")
    phone_entry = tk.Entry(add_window)
    phone_entry.grid(row=3, column=1)

    tk.Label(add_window, text="Service Type:").grid(row=4, column=0, pady=5, sticky="e")
    service_var = tk.StringVar()
    service_dropdown = ttk.Combobox(
        add_window,
        textvariable=service_var,
        values=["Haircut", "Wash & Blow Dry", "Colour", "Highlights", "Toner", "Consultation"]
    )
    service_dropdown.grid(row=4, column=1)
    service_dropdown.current(0)

    tk.Label(add_window, text="Appointment Date (DD/MM/YYYY):").grid(row=5, column=0, pady=5, sticky="e")
    appointment_entry = tk.Entry(add_window)
    appointment_entry.grid(row=5, column=1)

    def submit_add():
        valid, message = validate_inputs(
            first_name_entry.get(),
            last_name_entry.get(),
            email_entry.get(),
            phone_entry.get(),
            appointment_entry.get()
        )
        if not valid:
            messagebox.showerror("Invalid Input", message)
            return

        add_customer(
            first_name_entry.get(),
            last_name_entry.get(),
            email_entry.get(),
            phone_entry.get(),
            service_var.get(),
            appointment_entry.get()
        )
        messagebox.showinfo("Success", "Customer added successfully!")
        add_window.destroy()

    ctk.CTkButton(add_window, text="Add Customer", command=submit_add).grid(
        row=6, column=0, columnspan=2, pady=10
    )

# edit window (select first)
def open_edit_window():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a customer to edit")
        return

    item = tree.item(selected[0])
    customer_id, first_name, last_name, email, phone_number, service_type, appointment_date = item["values"]

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Customer")
    edit_window.geometry("450x250")
    edit_window.resizable(False,False)

    tk.Label(edit_window, text="First Name:").grid(row=0, column=0, pady=5, sticky="e")
    first_name_entry = tk.Entry(edit_window)
    first_name_entry.grid(row=0, column=1)
    first_name_entry.insert(0, first_name)

    tk.Label(edit_window, text="Last Name:").grid(row=1, column=0, pady=5, sticky="e")
    last_name_entry = tk.Entry(edit_window)
    last_name_entry.grid(row=1, column=1)
    last_name_entry.insert(0, last_name)

    tk.Label(edit_window, text="Email Address:").grid(row=2, column=0, pady=5, sticky="e")
    email_entry = tk.Entry(edit_window)
    email_entry.grid(row=2, column=1)
    email_entry.insert(0, email)

    tk.Label(edit_window, text="Phone Number:").grid(row=3, column=0, pady=5, sticky="e")
    phone_entry = tk.Entry(edit_window)
    phone_entry.grid(row=3, column=1)
    phone_entry.insert(0, phone_number)

    tk.Label(edit_window, text="Service Type:").grid(row=4, column=0, pady=5, sticky="e")
    service_var = tk.StringVar(value=service_type)
    service_dropdown = ttk.Combobox(
        edit_window,
        textvariable=service_var,
        values=["Haircut", "Wash & Blow Dry", "Colour", "Highlights", "Toner", "Consultation"]
    )
    service_dropdown.grid(row=4, column=1)

    tk.Label(edit_window, text="Appointment Date (DD/MM/YYYY):").grid(row=5, column=0, pady=5, sticky="e")
    appointment_entry = tk.Entry(edit_window)
    appointment_entry.grid(row=5, column=1)
    appointment_entry.insert(0, appointment_date)

    def save_edit():
        valid, message = validate_inputs(
            first_name_entry.get(),
            last_name_entry.get(),
            email_entry.get(),
            phone_entry.get(),
            appointment_entry.get()
        )
        if not valid:
            messagebox.showerror("Invalid Input", message)
            return

        update_customer(
            customer_id,
            first_name_entry.get(),
            last_name_entry.get(),
            email_entry.get(),
            phone_entry.get(),
            service_var.get(),
            appointment_entry.get()
        )
        messagebox.showinfo("Success", "Customer updated successfully!")
        edit_window.destroy()

    ctk.CTkButton(edit_window, text="Save Changes", command=save_edit).grid(
        row=6, column=0, columnspan=2, pady=10
    )


# add buttons to gui
ctk.CTkButton(frame, text="Add", command=open_add_window).grid(row=0, column=2, padx=5)
ctk.CTkButton(frame, text="Edit", command=open_edit_window).grid(row=0, column=3, padx=5)
ctk.CTkButton(
    frame,
    text="Delete",
    command=delete_customer,
    fg_color="#c0392b",
    hover_color="#922b21"
).grid(row=0, column=4, padx=5)
ctk.CTkButton(frame, text="Search", command=search_action).grid(row=0, column=5, padx=5)


# run program
root.mainloop()
