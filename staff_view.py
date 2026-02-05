import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import sqlite3
import re
import subprocess

DATABASE = "staff.db"

# initialise database
class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone_number TEXT UNIQUE,
                password TEXT
            )
        """)
        conn.commit()
        conn.close()

    def fetch_staff(self, search_term=""):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        if search_term:
            # only search first_name or last_name
            cursor.execute("""
                SELECT staff_id, first_name, last_name, email, phone_number
                FROM Staff
                WHERE first_name LIKE ? OR last_name LIKE ?
            """, ('%' + search_term + '%', '%' + search_term + '%'))
        else:
            cursor.execute("SELECT staff_id, first_name, last_name, email, phone_number FROM Staff")
        rows = cursor.fetchall()
        conn.close()
        return rows


    def add_staff(self, first, last, email, phone, password):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Staff (first_name, last_name, email, phone_number, password)
            VALUES (?, ?, ?, ?, ?)
        """, (first, last, email, phone, password))
        conn.commit()
        conn.close()

    def update_staff(self, staff_id, first, last, email, phone):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Staff SET first_name=?, last_name=?, email=?, phone_number=?
            WHERE staff_id=?
        """, (first, last, email, phone, staff_id))
        conn.commit()
        conn.close()

    def delete_staff(self, staff_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Staff WHERE staff_id=?", (staff_id,))
        conn.commit()
        conn.close()

    def update_password(self, staff_id, new_pass):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("UPDATE Staff SET password=? WHERE staff_id=?", (new_pass, staff_id))
        conn.commit()
        conn.close()

# phone number entry
class PhoneEntry(ctk.CTkEntry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar(value="+44")
        self.configure(textvariable=self.var)
        self.var.trace_add("write", self.validate)
    
    def validate(self, *args):
        value = self.var.get()
        # force +44 prefix
        if not value.startswith("+44"):
            self.var.set("+44")
            return
        # allow max of 13 characterss (+44 + 10 digits)
        if len(value) > 13:
            self.var.set(value[:13])
        # remove non-digits after +44
        prefix = "+44"
        digits = "".join(c for c in value[3:] if c.isdigit())
        self.var.set(prefix + digits)

# window for changing password
class PasswordChangeWindow(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, staff_id):
        super().__init__(parent)
        self.db_manager = db_manager
        self.staff_id = staff_id
        self.title("Change Password")
        self.geometry("400x200")
        self.resizable(False, False) #prevents window from being resizable

        ctk.CTkLabel(self, text="New Password:").grid(row=0, column=0, padx=10, pady=10)
        self.new_pass = ctk.CTkEntry(self, show="*")
        self.new_pass.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self, text="Confirm Password:").grid(row=1, column=0, padx=10, pady=10)
        self.confirm_pass = ctk.CTkEntry(self, show="*")
        self.confirm_pass.grid(row=1, column=1, padx=10, pady=10)

        self.show_var = tk.BooleanVar()
        ctk.CTkCheckBox(self, text="Show Passwords", variable=self.show_var, command=self.toggle_show).grid(row=2, column=0, columnspan=2)

        ctk.CTkButton(self, text="Update", command=self.update_password, fg_color="#2b8c4a").grid(row=3, column=0, columnspan=2, pady=10)

    def toggle_show(self):
        show = "" if self.show_var.get() else "*" # ex. password becomes ******** if 'show password' not ticked, revealed otherwise
        self.new_pass.configure(show=show)
        self.confirm_pass.configure(show=show)

    def update_password(self):
        p1 = self.new_pass.get()
        p2 = self.confirm_pass.get()
        if p1 != p2:
            messagebox.showerror("Error", "Passwords do not match") # if password field doesn't mmatch confirm password field, throw error
            return
        if len(p1) < 8 or not any(c.isupper() for c in p1) or not any(c.islower() for c in p1) or not any(c.isdigit() for c in p1):
            messagebox.showerror("Error", "Password must be 8+ chars with uppercase, lowercase and digit")
            return
        self.db_manager.update_password(self.staff_id, p1)
        messagebox.showinfo("Success", "Password updated")
        self.destroy()

# add+edit staff form
class StaffFormWindow(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, refresh_callback, staff_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback
        self.staff_data = staff_data
        self.title("Staff Form")
        self.geometry("400x350")
        self.resizable(False, False)

        self.entries = {}
        fields = ["First Name", "Last Name", "Email", "Phone Number"] #only fields available in edit window - password locked to adding
        for i, field in enumerate(fields):
            ctk.CTkLabel(self, text=field+":").grid(row=i, column=0, padx=10, pady=5)
            if field == "Phone Number":
                entry = PhoneEntry(self)
                if staff_data:
                    entry.var.set(staff_data[4])
            else:
                entry = ctk.CTkEntry(self)
                if staff_data:
                    entry.insert(0, staff_data[i+1])
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.entries[field] = entry

        # password fields only visible in add window
        if not staff_data:
            ctk.CTkLabel(self, text="Password:").grid(row=4, column=0, padx=10, pady=5)
            self.password = ctk.CTkEntry(self, show="*")
            self.password.grid(row=4, column=1, padx=10, pady=5)

            ctk.CTkLabel(self, text="Confirm Password:").grid(row=5, column=0, padx=10, pady=5)
            self.confirm_password = ctk.CTkEntry(self, show="*")
            self.confirm_password.grid(row=5, column=1, padx=10, pady=5)

        # buttons
        text = "Add Staff" if not staff_data else "Save Changes"
        ctk.CTkButton(self, text=text, command=self.save_staff, fg_color="#2b8c4a").grid(row=6, column=0, columnspan=2, pady=10)

        if staff_data:
            ctk.CTkButton(self, text="Change Password", command=self.open_password_change).grid(row=7, column=0, columnspan=2, pady=5)

    def open_password_change(self):
        PasswordChangeWindow(self, self.db_manager, self.staff_data[0])

    def validate_inputs(self, first, last, email, phone, password=None, confirm=None):
        errors = []
        if not first.isalpha():
            errors.append("First name must be letters only")
        if not last.isalpha():
            errors.append("Last name must be letters only")
        if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            errors.append("Invalid email")
        if not phone.startswith("+44") or len(phone) != 13:
            errors.append("Phone must be +44 + 10 digits")
        if password is not None:
            if password != confirm:
                errors.append("Passwords do not match")
            if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
                errors.append("Password must be 8+ chars with uppercase, lowercase, digit")
        return errors

    def save_staff(self):
        first = self.entries["First Name"].get()
        last = self.entries["Last Name"].get()
        email = self.entries["Email"].get()
        phone = self.entries["Phone Number"].get()

        if self.staff_data:  # edit
            errors = self.validate_inputs(first, last, email, phone)
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            self.db_manager.update_staff(self.staff_data[0], first, last, email, phone)
            messagebox.showinfo("Success", "Staff updated")
        else:  # add
            password = self.password.get()
            confirm = self.confirm_password.get()
            errors = self.validate_inputs(first, last, email, phone, password, confirm)
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            self.db_manager.add_staff(first, last, email, phone, password)
            messagebox.showinfo("Success", "Staff added")
        self.refresh_callback()
        self.destroy()

# window for admin login
class AdminLoginWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login")
        self.geometry("300x180")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        self.admin_id = ctk.CTkEntry(self)
        self.admin_id.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        self.admin_pass = ctk.CTkEntry(self, show="*")
        self.admin_pass.grid(row=1, column=1, padx=10, pady=5)

        self.show_var = tk.BooleanVar()
        ctk.CTkCheckBox(self, text="Show Password", variable=self.show_var, command=self.toggle_show).grid(row=2, column=0, columnspan=2)

        ctk.CTkButton(self, text="Login", command=self.verify).grid(row=3, column=0, columnspan=2, pady=10)

    def toggle_show(self):
        show = "" if self.show_var.get() else "*"
        self.admin_pass.configure(show=show)

    def verify(self):
        if self.admin_id.get() == "1" and self.admin_pass.get() == "Password1": #only one set admin user for coursework purpose
            self.parent.admin_mode = True
            self.parent.update_buttons()
            messagebox.showinfo("Success", "Admin privileges granted")
            self.destroy()
        else:
            messagebox.showerror("Error", "Invalid credentials")

# main app
class StaffManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.db = DatabaseManager(DATABASE)
        self.admin_mode = False
        self.title("Staff Manager")
        self.geometry("1000x600")
        self.resizable(False, False)

        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        header = ctk.CTkFrame(self)
        header.pack(fill="x", pady=5)

        try:
            img = Image.open("logo.png")
            img.thumbnail((150, 120))  # prevents squishing when adding more to frame
            self.logo_img = ImageTk.PhotoImage(img)
            ctk.CTkLabel(header, image=self.logo_img).pack(pady=(0, 10))
        except:
            ctk.CTkLabel(header, text="Logo not found").pack(pady=(0, 10))

        # back to main menu button
        ctk.CTkButton(header, text="Back to Main Menu", command=self.back_to_main).pack(pady=(0, 10))

        # buttons for admin actions
        admin_frame = ctk.CTkFrame(header)
        admin_frame.pack(pady=(0, 10))

        self.admin_login_btn = ctk.CTkButton(admin_frame, text="Login", command=self.open_admin_login)
        self.admin_logout_btn = ctk.CTkButton(admin_frame, text="Logout", command=self.logout_admin, state="disabled") #disabled unless logged in

        self.admin_login_btn.pack(side="left", padx=5)
        self.admin_logout_btn.pack(side="left", padx=5)

        # table
        columns = ("ID", "First Name", "Last Name", "Email", "Phone Number")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        # action(add+edit+delete) frame
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=10)

        # search bar+button
        ctk.CTkLabel(action_frame, text="Search:").grid(row=0, column=0, padx=(5,5))
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(action_frame, textvariable=self.search_var, width=150)
        self.search_entry.grid(row=0, column=1, padx=5)
        ctk.CTkButton(action_frame, text="Search", command=self.search_staff).grid(row=0, column=2, padx=(5,20))

        # add+edit+delete buttons in frame
        self.add_btn = ctk.CTkButton(action_frame, text="Add", command=self.add_staff, state="disabled")
        self.edit_btn = ctk.CTkButton(action_frame, text="Edit", command=self.edit_staff, state="disabled")
        self.delete_btn = ctk.CTkButton(action_frame, text="Delete", command=self.delete_staff, fg_color="#c0392b", hover_color="#922b21", state="disabled")

        self.add_btn.grid(row=0, column=3, padx=5)
        self.edit_btn.grid(row=0, column=4, padx=5)
        self.delete_btn.grid(row=0, column=5, padx=5)



    # change button states if signed in (admin)
    def update_buttons(self):
        state = "normal" if self.admin_mode else "disabled"
        self.add_btn.configure(state=state)
        self.edit_btn.configure(state=state)
        self.delete_btn.configure(state=state)
        self.admin_login_btn.configure(state="disabled" if self.admin_mode else "normal")
        self.admin_logout_btn.configure(state="normal" if self.admin_mode else "disabled")

    # admin
    def open_admin_login(self):
        AdminLoginWindow(self)

    def logout_admin(self):
        self.admin_mode = False
        self.update_buttons()
        messagebox.showinfo("Logged Out", "Admin privileges revoked")

    # back to main menu function
    def back_to_main(self):
        subprocess.Popen(["python3", "main_menu.py"])
        self.destroy()

    # refresh table for searching
    def refresh_table(self, search_term=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for staff in self.db.fetch_staff(search_term):
            self.tree.insert("", "end", values=staff)

    def search_staff(self):
        term = self.search_var.get().strip()
        self.refresh_table(term)

    # crud operations
    def add_staff(self):
        StaffFormWindow(self, self.db, self.refresh_table)

    def edit_staff(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a staff member to edit")
            return
        data = self.tree.item(selected[0])["values"]
        StaffFormWindow(self, self.db, self.refresh_table, staff_data=data)

    def delete_staff(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a staff member to delete")
            return
        data = self.tree.item(selected[0])["values"]
        confirm = messagebox.askyesno("Confirm", f"Delete {data[1]} {data[2]}?")
        if confirm:
            self.db.delete_staff(data[0])
            self.refresh_table()
            messagebox.showinfo("Deleted", f"{data[1]} {data[2]} deleted")

# run program
if __name__ == "__main__":
    app = StaffManagerApp()
    app.mainloop()
