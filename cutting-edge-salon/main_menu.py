## main menu after staff login

import customtkinter as ctk
from tkinter import messagebox
import subprocess
import os

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # get staff info from environment
        self.staff_name = os.environ.get('CURRENT_STAFF_NAME', 'Staff')
        self.is_admin = os.environ.get('CURRENT_STAFF_ADMIN', '0') == '1'
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(f"Main Menu - Welcome {self.staff_name}")
        self.geometry("500x550")
        self.resizable(False, False)
        
        self.center_window()
        self.build_ui()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def build_ui(self):
        # welcome message
        welcome = ctk.CTkLabel(self, text=f"Welcome, {self.staff_name}!",
                              font=ctk.CTkFont(size=24, weight="bold"))
        welcome.pack(pady=(30, 5))
        
        # admin badge
        if self.is_admin:
            ctk.CTkLabel(self, text="👑 Administrator", 
                        font=ctk.CTkFont(size=14),
                        text_color="gold").pack(pady=(0, 20))
        else:
            ctk.CTkLabel(self, text="Staff Member",
                        font=ctk.CTkFont(size=14)).pack(pady=(0, 20))
        
        # menu frame
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # buttons
        buttons = [
            ("👥 Customer Management", self.open_customer_view),
            ("📅 Customer Bookings", self.booking_placeholder),
            ("💰 Payments", self.payment_placeholder),
        ]
        
        # add staff management for admins
        if self.is_admin:
            buttons.append(("👥 Staff Management (Admin)", self.open_staff_view))
        
        for text, command in buttons:
            btn = ctk.CTkButton(menu_frame, text=text, command=command,
                               height=45, font=ctk.CTkFont(size=15))
            btn.pack(pady=8, padx=20, fill="x")
        
        # logout button
        logout_btn = ctk.CTkButton(self, text="🚪 Log Out", command=self.logout,
                                  height=40, width=150, fg_color="#c0392b")
        logout_btn.pack(pady=20)
    
    def open_customer_view(self):
        self.destroy()
        subprocess.Popen(["python3", "customer_view.py"])
    
    def open_staff_view(self):
        self.destroy()
        subprocess.Popen(["python3", "staff_view.py"])
    
    def booking_placeholder(self):
        messagebox.showinfo("Coming Soon", "Booking system coming in next update!")
    
    def payment_placeholder(self):
        messagebox.showinfo("Coming Soon", "Payment system coming in next update!")
    
    def logout(self):
        if messagebox.askyesno("Log Out", "Are you sure?"):
            # clear environment
            for key in ['CURRENT_STAFF_ID', 'CURRENT_STAFF_NAME', 'CURRENT_STAFF_ADMIN']:
                if key in os.environ:
                    del os.environ[key]
            self.destroy()
            subprocess.Popen(["python3", "welcome_window.py"])

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()