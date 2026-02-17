import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Management Dashboard", font=("Helvetica", 20)).pack(pady=20)

        ctk.CTkButton(self, text="Customer Management", 
                      command=lambda: self.controller.show_view("CustomerView")).pack(pady=10)
        
        ctk.CTkButton(self, text="Staff Management", 
                      command=lambda: self.controller.show_view("StaffView")).pack(pady=10)

        ctk.CTkButton(self, text="Logout", fg_color="red", 
                      command=lambda: self.controller.show_view("WelcomeView")).pack(pady=20)