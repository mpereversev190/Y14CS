import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import subprocess
from PIL import Image, ImageTk
import os


##create the actual database idiot
##also create a registration window

class DatabaseManager:
    """Handles all database operations"""
    DB_NAME = 'staff.db'
    
    @staticmethod
    def connect_db():
        return sqlite3.connect(DatabaseManager.DB_NAME)
    
    @staticmethod
    def init_database():
        """Initialize database with required tables"""
        with DatabaseManager.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Staff (
                                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                first_name TEXT NOT NULL,
                                last_name TEXT NOT NULL,
                                email TEXT UNIQUE NOT NULL,
                                phone_number TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL
                            )''')
            
            # Check if any staff exists, if not add a default one
            cursor.execute("SELECT COUNT(*) FROM Staff")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    "INSERT INTO Staff (first_name, last_name, email, phone_number, password) VALUES (?, ?, ?, ?, ?)",
                    ("Admin", "User", "admin@example.com", "+441234567890", "admin123")
                )
            conn.commit()
    
    @staticmethod
    def fetch_staff_ids():
        """Fetch all staff IDs from database"""
        with DatabaseManager.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT staff_id FROM Staff ORDER BY staff_id")
            return [str(row[0]) for row in cursor.fetchall()]
    
    @staticmethod
    def get_staff_by_id(staff_id):
        """Get staff details by ID"""
        with DatabaseManager.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name, password FROM Staff WHERE staff_id = ?", (staff_id,))
            return cursor.fetchone()


class LoginForm:
    """Login form for staff members"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("800x400")  # set window size
        self.root.title("Staff Login")
        
        self.main_frame = ctk.CTkFrame(master=self.root)
        self.main_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for login form"""
        # Main container frame
        container = ctk.CTkFrame(self.main_frame)
        container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Left frame for logo
        left_frame = ctk.CTkFrame(container)
        left_frame.grid(row=0, column=0, padx=(10, 10), pady=20, sticky="nsew")
        
        # Right frame for login fields
        right_frame = ctk.CTkFrame(container)
        right_frame.grid(row=0, column=1, padx=(10, 10), pady=20, sticky="nsew")
        
        # Configure grid weights
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Create logo in left frame
        self.create_logo(left_frame)
        
        # Create login fields in right frame
        self.create_login_fields(right_frame)
    
    def create_logo(self, parent_frame):
        """Load and display logo in the left frame"""
        title_label = ctk.CTkLabel(
            parent_frame,
            text="Welcome to Cutting Edge",
            font=('Arial', 24, 'bold'))
        title_label.pack(pady=(0, 0))
        
        try:
            if os.path.exists("logo.png"):
                image = Image.open("logo.png")
                resized_image = image.resize((250, 250))  
                self.logo_image = ctk.CTkImage(light_image=resized_image, size=(250, 250))
                
                self.logo_label = ctk.CTkLabel(
                    master=parent_frame, 
                    image=self.logo_image, 
                    text=""
                )
                self.logo_label.pack(expand=True)
        except Exception as e:
            error_label = ctk.CTkLabel(
                parent_frame,
                text="Logo Error"
            )
            error_label.pack(expand=True)
    
    def create_login_fields(self, parent_frame):
        """Create login fields in the right frame"""
        login_title = ctk.CTkLabel(
            parent_frame,
            text="Login",
            font=('Arial', 24, 'bold')
        )
        login_title.grid(row=0, column=0, columnspan=2, pady=(0, 40))
        
        # Staff ID dropdown
        ctk.CTkLabel(parent_frame, text="Staff ID:").grid(row=1, column=0, pady=10, sticky="e")
        
        self.staff_id_var = ctk.StringVar()
        self.update_staff_dropdown()
        
        self.staff_id_dropdown = ttk.Combobox(
            parent_frame, 
            textvariable=self.staff_id_var,
            values=self.staff_ids,
            state="readonly",
            width=25
        )
        self.staff_id_dropdown.grid(row=1, column=1, pady=10, padx=(10, 0), sticky="w")
        
        if self.staff_ids:
            self.staff_id_dropdown.current(0)
        
        # Password field
        ctk.CTkLabel(parent_frame, text="Password:", font=('Arial', 14)).grid(row=2, column=0, pady=10, sticky="e")
        
        self.password_entry = ctk.CTkEntry(
            parent_frame, 
            placeholder_text='Enter password', 
            show='*',
            width=150
        )
        self.password_entry.grid(row=2, column=1, pady=10, padx=(10, 0), sticky="w")
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar()
        self.show_password_check = ttk.Checkbutton(
            parent_frame,
            text='Show Password',
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_check.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Login button
        self.login_button = ttk.Button(button_frame, text="Login", command=self.login)
        self.login_button.grid(row=0, column=0, padx=10)
        
        # Exit button
        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_application)
        self.exit_button.grid(row=1, column=0, padx=10)
    
    def update_staff_dropdown(self):
        """Update dropdown with current staff IDs"""
        self.staff_ids = DatabaseManager.fetch_staff_ids()
        
        if not self.staff_ids:
            messagebox.showwarning("No Staff", "No staff records found in the database.")
            self.staff_ids = ["No staff available"]
        
        if hasattr(self, 'staff_id_dropdown') and self.staff_id_dropdown:
            self.staff_id_dropdown['values'] = self.staff_ids
            if self.staff_ids:
                self.staff_id_dropdown.current(0)
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
    
    def login(self):
        """Handle login attempt"""
        staff_id = self.staff_id_var.get()
        password = self.password_entry.get()
        
        if not staff_id or staff_id == "No staff available":
            messagebox.showerror("Error", "Please select a valid Staff ID")
            return
            
        if not password:
            messagebox.showerror("Error", "Please enter your password")
            return
        
        user = DatabaseManager.get_staff_by_id(staff_id)
        
        if user:
            stored_password = user[2]
            if password == stored_password:
                messagebox.showinfo("Success", f"Welcome {user[0]} {user[1]}!")
                self.root.destroy()
                try:
                    subprocess.Popen(["python", "main_menu.py"])
                except:
                    try:
                        subprocess.Popen(["python3", "main_menu.py"])
                    except:
                        messagebox.showinfo("Info", "Login successful!")
            else:
                messagebox.showerror("Error", "Invalid Password")
        else:
            messagebox.showerror("Error", "Invalid Staff ID")

    def exit_application(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()


def main():
    """Main application entry point"""
    DatabaseManager.init_database()
    app = LoginForm()
    app.root.mainloop()


if __name__ == '__main__':
    main()