import customtkinter as ctk
from tkinter import ttk, messagebox
import re

class CustomerView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_user_id = None

        # UI layout
        ctk.CTkLabel(self, text="Customer Management", font=("Helvetica", 20, "bold")).pack(pady=10)

        # search section
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
        self.email_var = ctk.StringVar()

        ctk.CTkEntry(form_frame, placeholder_text="First Name", textvariable=self.first_name_var).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkEntry(form_frame, placeholder_text="Last Name", textvariable=self.last_name_var).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkEntry(form_frame, placeholder_text="Email", textvariable=self.email_var).grid(row=0, column=2, padx=10, pady=10)

        # action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        ctk.CTkButton(btn_frame, text="Add Customer", fg_color="green", command=self.add_customer).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Update Selected", command=self.update_customer).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="red", command=self.delete_customer).pack(side="left", padx=5)

        # data table
        self.tree = ttk.Treeview(self, columns=("ID", "First Name", "Last Name", "Email"), show="headings")
        self.tree.heading("ID", text="ID", command=lambda: self.sort_column("ID", False))
        self.tree.heading("First Name", text="First Name", command=lambda: self.sort_column("First Name", False))
        self.tree.heading("Last Name", text="Last Name", command=lambda: self.sort_column("Last Name", False))
        self.tree.heading("Email", text="Email", command=lambda: self.sort_column("Email", False))
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        ctk.CTkButton(self, text="Back to Dashboard", command=lambda: self.controller.show_view("DashboardView")).pack(pady=10)

        self.refresh_data()

    # validation method

    def validate_inputs(self):
        fn = self.first_name_var.get().strip()
        ln = self.last_name_var.get().strip()
        em = self.email_var.get().strip()

        if not fn or not ln or not em:
            messagebox.showwarning("Invalid Input", "All fields are required.")
            return False

        if not fn.isalpha():
            messagebox.showwarning("Invalid Input", "First name must contain letters only.")
            return False

        if not ln.isalpha():
            messagebox.showwarning("Invalid Input", "Last name must contain letters only.")
            return False

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, em):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return False

        return True

    def sort_column(self, col, reverse):
        # get all rows
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        # try numeric sort, fallback to string
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        # rearrange rows
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

        # toggle sort order next click
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    # username generator

    def generate_unique_username(self, base_username):
        username = base_username
        counter = 1

        self.controller.db.cur.execute("SELECT username FROM users WHERE username=?", (username,))
        result = self.controller.db.cur.fetchone()

        while result is not None:
            username = f"{base_username}{counter}"
            counter += 1
            self.controller.db.cur.execute("SELECT username FROM users WHERE username=?", (username,))
            result = self.controller.db.cur.fetchone()

        return username

    # logic methods

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get()
        customers = self.controller.db.fetch_all_customers(search_term)
        
        for c in customers:
            self.tree.insert("", "end", values=(c[0], c[1], c[2], c[3]))

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.refresh_data()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item)['values']
        self.selected_user_id = values[0]
        self.first_name_var.set(values[1])
        self.last_name_var.set(values[2])
        self.email_var.set(values[3])

    def add_customer(self):
        if not self.validate_inputs():
            return

        fn, ln, em = self.first_name_var.get(), self.last_name_var.get(), self.email_var.get()

        base_username = em.split('@')[0] + "_user"
        username = self.generate_unique_username(base_username)
        password = self.controller.db.hash_password("password123")
        
        try:
            self.controller.db.cur.execute("""
                INSERT INTO users (username, password, email, first_name, last_name, role)
                VALUES (?, ?, ?, ?, ?, 'customer')
            """, (username, password, em, fn, ln))
            self.controller.db.conn.commit()
            self.refresh_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add user: {e}")

    def update_customer(self):
        if not self.selected_user_id:
            messagebox.showwarning("Selection", "Please select a customer to update")
            return

        if not self.validate_inputs():
            return
        
        try:
            self.controller.db.cur.execute("""
                UPDATE users SET first_name=?, last_name=?, email=? WHERE user_id=?
            """, (self.first_name_var.get(), self.last_name_var.get(), self.email_var.get(), self.selected_user_id))
            self.controller.db.conn.commit()
            self.refresh_data()
            messagebox.showinfo("Success", "Customer updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_customer(self):
        if not self.selected_user_id:
            return
        
        if messagebox.askyesno("Confirm", "Delete this customer?"):
            self.controller.db.delete_user(self.selected_user_id)
            self.refresh_data()
            self.clear_fields()

    def clear_fields(self):
        self.selected_user_id = None
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
