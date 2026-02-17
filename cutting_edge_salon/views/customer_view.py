import customtkinter as ctk
from tkinter import ttk

class CustomerView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Customer Database", font=("Helvetica", 18)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Email", "Last Visit"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Last Visit", text="Last Visit")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        self.refresh_data()

        ctk.CTkButton(self, text="Back to Dashboard", 
                      command=lambda: self.controller.show_view("DashboardView")).pack(pady=10)

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        customers = self.controller.db.fetch_all_customers()
        for c in customers:
            self.tree.insert("", "end", values=(c[0], f"{c[1]} {c[2]}", c[3], "N/A"))