import customtkinter as ctk
from tkinter import messagebox

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        # Clear anything that was there before
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="Management Dashboard", font=("Helvetica", 20)).pack(pady=20)

        print("DEBUG DASHBOARD: current_user =", self.controller.current_user)

        # -------------------------
        # CUSTOMER MANAGEMENT
        # staff + admin
        # -------------------------
        if self.controller.has_role("staff", "admin"):
            ctk.CTkButton(
                self, text="Customer Management",
                command=lambda: self.controller.show_view("CustomerView")
            ).pack(pady=10)

        # -------------------------
        # STAFF MANAGEMENT
        # admin only
        # -------------------------
        if self.controller.has_role("admin"):
            ctk.CTkButton(
                self, text="Staff Management",
                command=lambda: self.controller.show_view("StaffView")
            ).pack(pady=10)

            ctk.CTkButton(
                self, text="Create Staff Account",
                command=self.open_create_staff_popup
            ).pack(pady=10)

        # -------------------------
        # BOOKING MANAGEMENT
        # staff + admin
        # -------------------------
        if self.controller.has_role("staff", "admin"):
            ctk.CTkButton(
                self, text="Booking Management",
                command=lambda: self.controller.show_view("BookingView")
            ).pack(pady=10)

        # -------------------------
        # PAYMENT MANAGEMENT
        # admin only
        # -------------------------
        if self.controller.has_role("admin"):
            ctk.CTkButton(
                self, text="Payment Management",
                command=lambda: self.controller.show_view("PaymentView")
            ).pack(pady=10)

        # -------------------------
        # LOGOUT (everyone)
        # -------------------------
        ctk.CTkButton(
            self, text="Logout", fg_color="red",
            command=lambda: self.controller.show_view("WelcomeView")
        ).pack(pady=20)

    def refresh_data(self):
        # Called every time DashboardView is shown
        self.build_ui()

    def open_create_staff_popup(self):
        CreateStaffPopup(self.controller)


# -------------------------------------------------------
# POPUP WINDOW CLASS (STAFF CREATION)
# -------------------------------------------------------
class CreateStaffPopup(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.title("Create Staff Account")
        self.geometry("400x420")

        ctk.CTkLabel(self, text="Create Staff Account", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Variables
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.first_var = ctk.StringVar()
        self.last_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()

        # Form fields
        ctk.CTkEntry(self, placeholder_text="Username", textvariable=self.username_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Password", textvariable=self.password_var, show="*").pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="First Name", textvariable=self.first_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Last Name", textvariable=self.last_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Email", textvariable=self.email_var).pack(pady=5)
        ctk.CTkEntry(self, placeholder_text="Phone Number", textvariable=self.phone_var).pack(pady=5)

        ctk.CTkButton(self, text="Create Staff", fg_color="green", command=self.create_staff).pack(pady=15)

    def create_staff(self):
        username = self.username_var.get()
        password = self.password_var.get()
        first = self.first_var.get()
        last = self.last_var.get()
        email = self.email_var.get()
        phone = self.phone_var.get()

        if not username or not password:
            messagebox.showwarning("Missing Information", "Username and password are required.")
            return

        hashed_pw = self.controller.db.hash_password(password)

        try:
            self.controller.db.cur.execute("""
                INSERT INTO users (username, password, first_name, last_name, email, phone_number, role)
                VALUES (?, ?, ?, ?, ?, ?, 'staff')
            """, (username, hashed_pw, first, last, email, phone))

            self.controller.db.conn.commit()
            messagebox.showinfo("Success", "Staff account created successfully.")
            self.destroy()  # close popup

        except Exception as e:
            messagebox.showerror("Error", f"Could not create staff: {e}")
