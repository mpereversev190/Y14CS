import customtkinter as ctk
from tkinter import messagebox
from PIL import Image 
import os            

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # logo loading
        try:
            # looks for logo file in same directory as code
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(base_dir, "assets", "logo.png")

            # image
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(150, 150)
            )

            # display the image in a label
            self.logo_label = ctk.CTkLabel(self, image=self.logo_img, text="")
            self.logo_label.pack(pady=(20, 0)) # spacing at the top
        except Exception as e:
            print(f"DEBUG: Logo could not be loaded: {e}")
            # if the logo fails, the app will still run without crashing

        # GUI
        ctk.CTkLabel(self, text="Staff Login", font=("Helvetica", 24, "bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=200)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=200)
        self.password_entry.pack(pady=10)

        self.btn = ctk.CTkButton(self, text="Login", command=self.attempt_login, corner_radius=10)
        self.btn.pack(pady=20)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        print(f"DEBUG: Trying to login with '{username}' and '{password}'")
        
        user = self.controller.db.login(username, password)
        
        if user:
            print("DEBUG: Success!")
            self.controller.show_view("DashboardView")
        else:
            print("DEBUG: Failed!")
            messagebox.showerror("Error", "Invalid credentials")