import customtkinter as ctk
from tkinter import messagebox

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="Management Dashboard", font=("Helvetica", 20)).pack(pady=20)

        print("DEBUG DASHBOARD: current_user =", self.controller.current_user)

        # customer management
        if self.controller.has_role("staff", "admin"):
            ctk.CTkButton(
                self, text="Customer Management",
                command=lambda: self.controller.show_view("CustomerView")
            ).pack(pady=10)

        # staff management (locked behind admin role)
        if self.controller.has_role("admin"):
            ctk.CTkButton(
                self, text="Staff Management",
                command=lambda: self.controller.show_view("StaffView")
            ).pack(pady=10)

            ctk.CTkButton(
                self, text="Create Staff Account",
                command=self.open_create_staff_popup
            ).pack(pady=10)

        # booking management
        if self.controller.has_role("staff", "admin"):
            ctk.CTkButton(
                self, text="Booking Management",
                command=lambda: self.controller.show_view("BookingView")
            ).pack(pady=10)

        # payment management (locked behind admin role)
        if self.controller.has_role("admin"):
            ctk.CTkButton(
                self, text="Payment Management",
                command=lambda: self.controller.show_view("PaymentView")
            ).pack(pady=10)

        # logout
        ctk.CTkButton(
            self, text="Logout", fg_color="red",
            command=lambda: self.controller.show_view("WelcomeView")
        ).pack(pady=20)

    def refresh_data(self):
        self.build_ui()

    def open_create_staff_popup(self):
        CreateStaffPopup(self.controller)


# popup for new user creation
class CreateStaffPopup(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.title("Create Staff Account")
        self.geometry("400x420")

        ctk.CTkLabel(self, text="Create Staff Account", font=("Helvetica", 18, "bold")).pack(pady=10)

        #variables
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.first_var = ctk.StringVar()
        self.last_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()

        #form fields
        ctk.CTkEntry(self, placeholder_text="Username", textvariable=self.username_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Password", textvariable=self.password_var, show="*").pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="First Name", textvariable=self.first_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Last Name", textvariable=self.last_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Email", textvariable=self.email_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Phone Number", textvariable=self.phone_var).pack(pady=5)

        ctk.CTkButton(self, text="Create Staff", fg_color="green", command=self.create_staff).pack(pady=15)

    def create_staff(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        first = self.first_var.get().strip()
        last = self.last_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()

        # empty field check
        if not username or not password or not first or not last or not email or not phone:
            messagebox.showwarning("Missing Information", "All fields are required.")
            return

        # password validation
        if len(password) < 6:
            messagebox.showwarning("Weak Password", "Password must be at least 6 characters long.")
            return

        # email validation
        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return

        # phone validation
        if not phone.isdigit():
            messagebox.showwarning("Invalid Phone Number", "Phone number must contain digits only.")
            return

        if len(phone) != 11:
            messagebox.showwarning("Invalid Phone Number", "Phone number must be exactly 11 digits.")
            return

        if not phone.startswith("07"):
            messagebox.showwarning("Invalid Phone Number", "Phone number must start with '07'.")
            return

        # hash password+insert
        hashed_pw = self.controller.db.hash_password(password)

        try:
            self.controller.db.cur.execute("""
                INSERT INTO users (username, password, first_name, last_name, email, phone_number, role)
                VALUES (?, ?, ?, ?, ?, ?, 'staff')
            """, (username, hashed_pw, first, last, email, phone))

            self.controller.db.conn.commit()
            messagebox.showinfo("Success", "Staff account created successfully.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Could not create staff: {e}")
