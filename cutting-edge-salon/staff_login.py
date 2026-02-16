## staff login with hashed passwords

import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import subprocess
from PIL import Image, ImageTk
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

## database setup
def init_db():
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    
    # Create staff table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            last_login TEXT
        )
    """)
    
    # Check if any staff exists
    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        # Create default admin (password: Admin@123)
        password = "Admin@123"
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        cursor.execute("""
            INSERT INTO staff (first_name, last_name, email, phone_number, password_hash, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Admin", "User", "admin@example.com", "+44 1234 567890", hashed.decode('utf-8'), 1))
        print("Default admin created - ID: 1, Password: Admin@123")
    
    conn.commit()
    conn.close()

init_db()

## database functions
def get_staff_ids():
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    cursor.execute("SELECT staff_id FROM staff WHERE is_active = 1 OR is_active IS NULL ORDER BY staff_id")
    ids = [str(row[0]) for row in cursor.fetchall()]
    conn.close()
    return ids

def get_staff_by_id(staff_id):
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT staff_id, first_name, last_name, password_hash, is_admin 
        FROM staff WHERE staff_id = ?
    """, (staff_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_last_login(staff_id):
    conn = sqlite3.connect("salon.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE staff SET last_login = datetime('now') WHERE staff_id = ?", (staff_id,))
    conn.commit()
    conn.close()

## login window
class LoginWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        self.title("Staff Login")
        self.geometry("800x400")
        
        # center window
        self.center_window()
        
        # setup main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # create widgets
        self.create_widgets()
        
        # bind enter key
        self.bind('<Return>', lambda e: self.login())
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        # container for left/right split
        container = ctk.CTkFrame(self.main_frame)
        container.pack(fill='both', expand=True)
        
        # left frame - logo
        left_frame = ctk.CTkFrame(container)
        left_frame.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")
        
        # right frame - login
        right_frame = ctk.CTkFrame(container)
        right_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")
        
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # logo
        ctk.CTkLabel(left_frame, text="Welcome to Cutting Edge", 
                    font=('Arial', 24, 'bold')).pack(pady=(20,10))
        
        try:
            if os.path.exists("logo.png"):
                img = Image.open("logo.png")
                img = img.resize((250, 250))
                logo_img = ctk.CTkImage(light_image=img, size=(250, 250))
                ctk.CTkLabel(left_frame, image=logo_img, text="").pack(expand=True)
        except:
            ctk.CTkLabel(left_frame, text="Logo Error").pack()
        
        # login form
        ctk.CTkLabel(right_frame, text="Staff Login", 
                    font=('Arial', 24, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,40))
        
        # staff id dropdown
        ctk.CTkLabel(right_frame, text="Staff ID:").grid(row=1, column=0, pady=10, sticky="e")
        
        self.staff_ids = get_staff_ids()
        self.staff_id_var = ctk.StringVar()
        
        self.id_dropdown = ttk.Combobox(right_frame, textvariable=self.staff_id_var,
                                       values=self.staff_ids, state="readonly", width=25)
        self.id_dropdown.grid(row=1, column=1, pady=10, padx=10, sticky="w")
        
        if self.staff_ids:
            self.id_dropdown.current(0)
        
        # password
        ctk.CTkLabel(right_frame, text="Password:").grid(row=2, column=0, pady=10, sticky="e")
        
        self.password_entry = ctk.CTkEntry(right_frame, placeholder_text='Enter password', 
                                          show='*', width=180)
        self.password_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")
        
        # show password checkbox
        self.show_var = ctk.BooleanVar()
        self.show_check = ttk.Checkbutton(right_frame, text='Show Password',
                                         variable=self.show_var,
                                         command=self.toggle_password)
        self.show_check.grid(row=3, column=0, columnspan=2, pady=10)
        
        # buttons
        btn_frame = ctk.CTkFrame(right_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.login_btn = ttk.Button(btn_frame, text="Login", command=self.login)
        self.login_btn.grid(row=0, column=0, padx=10)
        
        self.exit_btn = ttk.Button(btn_frame, text="Exit", command=self.exit_app)
        self.exit_btn.grid(row=0, column=1, padx=10)
    
    def toggle_password(self):
        if self.show_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
    
    def login(self):
        staff_id = self.staff_id_var.get()
        password = self.password_entry.get()
        
        if not staff_id or staff_id == "No staff available":
            messagebox.showerror("Error", "Select a staff ID")
            return
        
        if not password:
            messagebox.showerror("Error", "Enter your password")
            return
        
        # get staff from database
        staff = get_staff_by_id(staff_id)
        
        if staff:
            stored_hash = staff[3]
            # verify password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # update last login
                update_last_login(staff_id)
                
                # set environment variables for other windows
                os.environ['CURRENT_STAFF_ID'] = str(staff[0])
                os.environ['CURRENT_STAFF_NAME'] = f"{staff[1]} {staff[2]}"
                os.environ['CURRENT_STAFF_ADMIN'] = str(staff[4])
                
                messagebox.showinfo("Success", f"Welcome {staff[1]} {staff[2]}!")
                
                # open main menu
                self.destroy()
                subprocess.Popen(["python3", "main_menu.py"])
            else:
                messagebox.showerror("Error", "Invalid password")
        else:
            messagebox.showerror("Error", "Invalid staff ID")
    
    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure?"):
            self.destroy()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()