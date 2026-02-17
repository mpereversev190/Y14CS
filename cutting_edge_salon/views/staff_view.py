import customtkinter as ctk
from tkinter import ttk

class StaffView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Staff Directory", font=("Helvetica", 18)).pack(pady=10)

        # Treeview for Data
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Role", "Phone"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Phone", text="Phone")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        self.refresh_data()

        ctk.CTkButton(self, text="Back to Dashboard", 
                      command=lambda: self.controller.show_view("DashboardView")).pack(pady=10)

    def refresh_data(self):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Fetch from DB (your shared instance)
        staff_members = self.controller.db.fetch_all_staff()
        for s in staff_members:
            # Assuming DB returns: (id, first, last, email, phone)
            self.tree.insert("", "end", values=(s[0], f"{s[1]} {s[2]}", "Stylist", s[4]))