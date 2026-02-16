## staff management - admin only
## note: requires admin login first

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import sqlite3
import re
import subprocess
import os
import bcrypt

DATABASE = "salon.db"

# get current staff from env
CURRENT_STAFF_ID = os.environ.get('CURRENT_STAFF_ID', '0')
CURRENT_STAFF_ADMIN = os.environ.get('CURRENT_STAFF_ADMIN', '0')

# check if admin
if CURRENT_STAFF_ADMIN != '1':
    messagebox.showerror("Access Denied", "Admin privileges required")
    exit()

## database functions
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

init_db()

def fetch_staff(search_term=""):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if search_term:
        cursor.execute("""
            SELECT staff_id, first_name, last_name, email, phone_number,
                   CASE WHEN is_admin=1 THEN 'Yes' ELSE 'No' END as admin
            FROM staff
            WHERE is_active=1 AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)
        """, ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
    else:
        cursor.execute("""
            SELECT staff_id, first_name, last_name, email, phone_number,
                   CASE WHEN is_admin=1 THEN 'Yes' ELSE 'No' END as admin
            FROM staff
            WHERE is_active=1
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_staff(first, last, email, phone, password, is_admin):
    # hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO staff (first_name, last_name, email, phone_number, password_hash, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first, last, email, phone, hashed.decode('utf-8'), 1 if is_admin else 0))
        conn.commit()
        success = True
    except sqlite3.IntegrityError as e:
        messagebox.showerror("Error", "Email or phone already exists")
        success = False
    conn.close()
    return success

def update_staff(staff_id, first, last, email, phone, is_admin):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE staff 
            SET first_name=?, last_name=?, email=?, phone_number=?, is_admin=?
            WHERE staff_id=?
        """, (first, last, email, phone, 1 if is_admin else 0, staff_id))
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success

def delete_staff(staff_id):
    # soft delete - just mark inactive
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE staff SET is_active=0 WHERE staff_id=?", (staff_id,))
    conn.commit()
    conn.close()

def update_password(staff_id, new_pass):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_pass.encode('utf-8'), salt)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE staff SET password_hash=? WHERE staff_id=?", (hashed.decode('utf-8'), staff_id))
    conn.commit()
    conn.close()

## validation
def validate_name(name):
    return re.match(r"^[A-Za-z\s\-']+$", name)

def validate_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def validate_phone(phone):
    if not phone:
        return True
    return re.match(r"^\+44\s?\d{4}\s?\d{6}$", phone) or \
           re.match(r"^07\d{3}\s?\d{6}$", phone) or \
           re.match(r"^0\d{2,4}\s?\d{6}$", phone)

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password needs an uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password needs a lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password needs a number"
    return True, ""

## password change window
class PasswordChangeWindow(ctk.CTkToplevel):
    def __init__(self, parent, staff_id, staff_name):
        super().__init__(parent)
        
        self.staff_id = staff_id
        self.parent = parent
        
        self.title(f"Change Password - {staff_name}")
        self.geometry("400x250")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # password requirements
        req_text = "Password must have:\n• 8+ characters\n• Uppercase letter\n• Lowercase letter\n• Number"
        ctk.CTkLabel(self, text=req_text, justify="left").pack(pady=10, padx=20)
        
        # new password
        ctk.CTkLabel(self, text="New Password:").pack()
        self.new_pass = ctk.CTkEntry(self, show="*", width=200)
        self.new_pass.pack(pady=5)
        
        # confirm
        ctk.CTkLabel(self, text="Confirm Password:").pack()
        self.confirm_pass = ctk.CTkEntry(self, show="*", width=200)
        self.confirm_pass.pack(pady=5)
        
        # show password checkbox
        self.show_var = ctk.BooleanVar()
        self.show_check = ctk.CTkCheckBox(self, text="Show Passwords",
                                         variable=self.show_var,
                                         command=self.toggle_show)
        self.show_check.pack(pady=5)
        
        # buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Update", command=self.update_pass,
                     fg_color="#2b8c4a").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)
    
    def toggle_show(self):
        show = "" if self.show_var.get() else "*"
        self.new_pass.configure(show=show)
        self.confirm_pass.configure(show=show)
    
    def update_pass(self):
        p1 = self.new_pass.get()
        p2 = self.confirm_pass.get()
        
        if p1 != p2:
            messagebox.showerror("Error", "Passwords don't match")
            return
        
        valid, msg = validate_password(p1)
        if not valid:
            messagebox.showerror("Error", msg)
            return
        
        update_password(self.staff_id, p1)
        messagebox.showinfo("Success", "Password updated")
        self.destroy()
        self.parent.refresh_table()

## add/edit staff window
class StaffFormWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback, staff_data=None):
        super().__init__(parent)
        
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.staff_data = staff_data
        
        title = "Edit Staff" if staff_data else "Add New Staff"
        self.title(title)
        self.geometry("450x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # form fields
        row = 0
        
        ctk.CTkLabel(self, text="First Name:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.first_entry = ctk.CTkEntry(self, width=250)
        self.first_entry.grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        ctk.CTkLabel(self, text="Last Name:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.last_entry = ctk.CTkEntry(self, width=250)
        self.last_entry.grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        ctk.CTkLabel(self, text="Email:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.email_entry = ctk.CTkEntry(self, width=250)
        self.email_entry.grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        ctk.CTkLabel(self, text="Phone:").grid(row=row, column=0, padx=10, pady=8, sticky="e")
        self.phone_entry = ctk.CTkEntry(self, width=250, placeholder_text="+44 7123 456789")
        self.phone_entry.grid(row=row, column=1, padx=10, pady=8)
        row += 1
        
        # admin checkbox
        self.admin_var = ctk.BooleanVar()
        self.admin_check = ctk.CTkCheckBox(self, text="Administrator Privileges",
                                          variable=self.admin_var)
        self.admin_check.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # password fields (only for add)
        if not staff_data:
            ctk.CTkLabel(self, text="Password:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
            self.pass_entry = ctk.CTkEntry(self, show="*", width=250)
            self.pass_entry.grid(row=row, column=1, padx=10, pady=8)
            row += 1
            
            ctk.CTkLabel(self, text="Confirm Password:*").grid(row=row, column=0, padx=10, pady=8, sticky="e")
            self.confirm_entry = ctk.CTkEntry(self, show="*", width=250)
            self.confirm_entry.grid(row=row, column=1, padx=10, pady=8)
            row += 1
        
        # fill data if editing
        if staff_data:
            self.first_entry.insert(0, staff_data[1])
            self.last_entry.insert(0, staff_data[2])
            self.email_entry.insert(0, staff_data[3])
            self.phone_entry.insert(0, staff_data[4] or "")
            self.admin_var.set(True if staff_data[5] == 'Yes' else False)
        
        # buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        btn_text = "Save Changes" if staff_data else "Add Staff"
        ctk.CTkButton(btn_frame, text=btn_text, command=self.save,
                     fg_color="#2b8c4a").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)
        
        # password change button for edit
        if staff_data:
            ctk.CTkButton(self, text="Change Password", 
                         command=lambda: PasswordChangeWindow(self, staff_data[0], 
                                                             f"{staff_data[1]} {staff_data[2]}"),
                         fg_color="gray").grid(row=row+1, column=0, columnspan=2, pady=5)
    
    def save(self):
        first = self.first_entry.get().strip()
        last = self.last_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        is_admin = self.admin_var.get()
        
        # validate
        if not validate_name(first):
            messagebox.showerror("Error", "Invalid first name")
            return
        if not validate_name(last):
            messagebox.showerror("Error", "Invalid last name")
            return
        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email")
            return
        if phone and not validate_phone(phone):
            messagebox.showerror("Error", "Invalid UK phone number")
            return
        
        if self.staff_data:  # edit
            if update_staff(self.staff_data[0], first, last, email, phone, is_admin):
                messagebox.showinfo("Success", "Staff updated")
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Error", "Email already exists")
        else:  # add
            password = self.pass_entry.get()
            confirm = self.confirm_entry.get()
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords don't match")
                return
            
            valid, msg = validate_password(password)
            if not valid:
                messagebox.showerror("Error", msg)
                return
            
            if add_staff(first, last, email, phone, password, is_admin):
                messagebox.showinfo("Success", "Staff added")
                self.refresh_callback()
                self.destroy()

## main window
class StaffManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        self.title("Staff Manager (Admin)")
        self.geometry("1000x600")
        
        # configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.build_ui()
        self.refresh_table()
    
    def build_ui(self):
        # header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        
        # logo
        try:
            img = Image.open("logo.png")
            img = img.resize((80, 80))
            self.logo_img = ImageTk.PhotoImage(img)
            ctk.CTkLabel(header, image=self.logo_img).grid(row=0, column=0, padx=10)
        except:
            ctk.CTkLabel(header, text="🏢", font=("Arial", 40)).grid(row=0, column=0, padx=10)
        
        ctk.CTkLabel(header, text="Staff Management (Admin Only)",
                    font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=1, padx=10, sticky="w")
        
        # back button
        ctk.CTkButton(header, text="← Back to Menu", 
                     command=self.back_to_menu, width=120).grid(row=0, column=2, padx=10)
        
        # search bar
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Name or email...", width=300)
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        ctk.CTkButton(search_frame, text="Search", command=self.search).grid(row=0, column=2, padx=5)
        ctk.CTkButton(search_frame, text="Clear", command=self.clear_search,
                     fg_color="gray").grid(row=0, column=3, padx=5)
        
        # action buttons
        ctk.CTkButton(search_frame, text="➕ Add", command=self.add_staff,
                     fg_color="#2b8c4a").grid(row=0, column=4, padx=5)
        ctk.CTkButton(search_frame, text="✏️ Edit", command=self.edit_staff).grid(row=0, column=5, padx=5)
        ctk.CTkButton(search_frame, text="🗑️ Delete", command=self.delete_staff,
                     fg_color="#c0392b").grid(row=0, column=6, padx=5)
        
        # treeview
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("ID", "First Name", "Last Name", "Email", "Phone", "Admin")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Email" else 200)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        
        # double-click to edit
        self.tree.bind('<Double-1>', lambda e: self.edit_staff())
    
    def refresh_table(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for staff in fetch_staff(search_term):
            self.tree.insert("", "end", values=staff)
    
    def search(self):
        self.refresh_table(self.search_entry.get().strip())
    
    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.refresh_table()
    
    def add_staff(self):
        StaffFormWindow(self, self.refresh_table)
    
    def edit_staff(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a staff member to edit")
            return
        data = self.tree.item(selected[0])['values']
        StaffFormWindow(self, self.refresh_table, staff_data=data)
    
    def delete_staff(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a staff member to delete")
            return
        
        data = self.tree.item(selected[0])['values']
        name = f"{data[1]} {data[2]}"
        
        if data[0] == CURRENT_STAFF_ID:
            messagebox.showerror("Error", "You cannot delete yourself")
            return
        
        confirm = messagebox.askyesno("Confirm", f"Delete {name}?")
        if confirm:
            delete_staff(data[0])
            self.refresh_table()
            messagebox.showinfo("Success", f"{name} deleted")
    
    def back_to_menu(self):
        self.destroy()
        subprocess.Popen(["python3", "main_menu.py"])

if __name__ == "__main__":
    app = StaffManagerApp()
    app.mainloop()