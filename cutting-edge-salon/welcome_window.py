## main welcome screen - entry point for app

import customtkinter as ctk
import subprocess
import os
from PIL import Image, ImageTk

class WelcomeWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("Cutting Edge Salon - Welcome")
        self.geometry("500x450")
        self.resizable(False, False)
        
        # center window
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
        # title
        title = ctk.CTkLabel(self, text="Cutting Edge Salon", 
                            font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(30, 10))
        
        # logo
        try:
            img = Image.open("logo.png")
            img = img.resize((150, 150))
            self.logo_img = ImageTk.PhotoImage(img)
            ctk.CTkLabel(self, image=self.logo_img).pack(pady=10)
        except:
            ctk.CTkLabel(self, text="🏢", font=("Arial", 80)).pack(pady=10)
        
        # subtitle
        ctk.CTkLabel(self, text="Management System", 
                    font=ctk.CTkFont(size=16)).pack(pady=(0, 20))
        
        # buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        # book appointment (placeholder for now)
        booking_btn = ctk.CTkButton(btn_frame, text="📅 Book an Appointment",
                                   command=self.booking_placeholder,
                                   height=50, width=250, font=ctk.CTkFont(size=16))
        booking_btn.pack(pady=10)
        
        # staff login
        staff_btn = ctk.CTkButton(btn_frame, text="👤 Staff Login",
                                 command=self.open_staff_login,
                                 height=50, width=250, font=ctk.CTkFont(size=16))
        staff_btn.pack(pady=10)
        
        # exit
        exit_btn = ctk.CTkButton(btn_frame, text="Exit", command=self.quit,
                                height=40, width=150, fg_color="gray")
        exit_btn.pack(pady=20)
    
    def booking_placeholder(self):
        from tkinter import messagebox
        messagebox.showinfo("Coming Soon", "Online booking coming in next update!")
    
    def open_staff_login(self):
        self.destroy()
        subprocess.Popen(["python3", "staff_login.py"])

if __name__ == "__main__":
    app = WelcomeWindow()
    app.mainloop()