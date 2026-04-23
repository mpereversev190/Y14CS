import customtkinter as ctk
from tkinter import ttk, messagebox
import re

class StaffView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_staff_id = None

        # build UI once
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Staff Directory", font=("Helvetica", 20, "bold")).pack(pady=10)

        # search bar
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=20, pady=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by name...")
        self.search_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        ctk.CTkButton(search_frame, text="Search", width=100, command=self.refresh_data).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Clear", width=100, fg_color="gray", command=self.clear_search).pack(side="left", padx=5)

        # input form
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=20, pady=10)

        self.first_name_var = ctk.StringVar()
        self.last_name_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()

        ctk.CTkEntry(form_frame, placeholder_text="First Name", textvariable=self.first_name_var).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkEntry(form_frame, placeholder_text="Last Name", textvariable=self.last_name_var).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkEntry(form_frame, placeholder_text="Phone Number", textvariable=self.phone_var).grid(row=0, column=2, padx=10, pady=10)

        # action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        ctk.CTkButton(btn_frame, text="Add Staff", fg_color="green", command=self.add_staff).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Update Selected", command=self.update_staff).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="red", command=self.delete_staff).pack(side="left", padx=5)

        # table
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Email Address", "Phone"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Email Address", text="Email Address")
        self.tree.heading("Phone", text="Phone")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        ctk.CTkButton(self, text="Back to Dashboard",
                      command=lambda: self.controller.show_view("DashboardView")).pack(pady=10)

    def refresh_data(self):
        # access check (admin role)
        if not self.controller.has_role("admin"):
            messagebox.showerror("Access Denied", "Only admins can access Staff Management.")
            self.controller.show_view("DashboardView")
            return

        # clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_entry.get()
        staff_members = self.controller.db.fetch_all_staff(search_term)

        for s in staff_members:
            full_name = f"{s[1]} {s[2]}"
            self.tree.insert("", "end", values=(s[0], full_name, s[3], s[4]))


    # validation

    def validate_inputs(self):
        fn = self.first_name_var.get().strip()
        ln = self.last_name_var.get().strip()
        ph = self.phone_var.get().strip()

        if not fn or not ln or not ph: #if a field not filled in
            messagebox.showwarning("Invalid Input", "All fields are required.")
            return False

        if not fn.isalpha(): #if other than alphabetical characters 
            messagebox.showwarning("Invalid Input", "First name must contain letters only.")
            return False

        if not ln.isalpha(): #same as above
            messagebox.showwarning("Invalid Input", "Last name must contain letters only.")
            return False

        if not re.match(r"^\+?\d{7,15}$", ph): #if doesn't fall within length requirement
            messagebox.showwarning("Invalid Phone", "Phone must be 7–15 digits.")
            return False

        return True

    # refresh table

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_entry.get()
        staff_members = self.controller.db.fetch_all_staff(search_term)

        for s in staff_members:
            full_name = f"{s[1]} {s[2]}"
            self.tree.insert("", "end", values=(s[0], full_name, s[3], s[4]))

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.refresh_data()

    # row selection

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected)['values']
        self.selected_staff_id = values[0]

        name = values[1].split(" ")
        self.first_name_var.set(name[0])
        self.last_name_var.set(name[1] if len(name) > 1 else "")
        self.phone_var.set(values[3])

    # add staff

    def add_staff(self):
        if not self.validate_inputs():
            return

        fn, ln, ph = self.first_name_var.get(), self.last_name_var.get(), self.phone_var.get()

        # generate a username from first+last
        base_username = (fn + ln).lower()
        username = base_username
        counter = 1

        # ensure unique username
        self.controller.db.cur.execute("SELECT username FROM users WHERE username=?", (username,))
        while self.controller.db.cur.fetchone():
            username = f"{base_username}{counter}"
            counter += 1
            self.controller.db.cur.execute("SELECT username FROM users WHERE username=?", (username,))

        password = self.controller.db.hash_password("password123")

        try:
            self.controller.db.cur.execute("""
                INSERT INTO users (username, password, email, first_name, last_name, phone_number, role, status)
                VALUES (?, ?, ?, ?, ?, ?, 'staff', 'active')
            """, (username, password, f"{username}@salon.com", fn, ln, ph))

            self.controller.db.conn.commit()
            self.refresh_data()
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add staff: {e}")


    # update staff

    def update_staff(self):
        if not self.selected_staff_id:
            messagebox.showwarning("Selection", "Please select a staff member to update.")
            return

        if not self.validate_inputs():
            return

        try:
            self.controller.db.cur.execute("""
                UPDATE users 
                SET first_name=?, last_name=?, phone_number=?
                WHERE user_id=?
            """, (
                self.first_name_var.get(),
                self.last_name_var.get(),
                self.phone_var.get(),
                self.selected_staff_id
            ))

            self.controller.db.conn.commit()
            self.refresh_data()
            messagebox.showinfo("Success", "Staff updated.")

        except Exception as e:
            messagebox.showerror("Error", str(e))


    # delete staff

    def delete_staff(self):
        if not self.selected_staff_id:
            return

        if messagebox.askyesno("Confirm", "Delete this staff member?"):
            try:
                self.controller.db.cur.execute("DELETE FROM users WHERE user_id=?", (self.selected_staff_id,))
                self.controller.db.conn.commit()

                self.refresh_data()
                self.clear_fields()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    # clear

    def clear_fields(self):
        self.selected_staff_id = None
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.phone_var.set("")

def refresh_data(self):
    if not self.controller.has_role("admin"):
        self.controller.show_view("DashboardView")
        return
