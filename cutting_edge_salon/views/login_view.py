import customtkinter as ctk
from tkinter import messagebox
from PIL import Image  # Required for high-quality image scaling
import os              # Required to find the file path on your Mac

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- LOGO LOADING LOGIC ---
        try:
            # This finds the 'assets' folder relative to this file
            # Go up one level from 'views' to the project root, then into 'assets'
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(base_dir, "assets", "logo.png")

            # Create the image object
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(150, 150) # You can adjust this size to fit her design
            )

            # Display the image in a label
            self.logo_label = ctk.CTkLabel(self, image=self.logo_img, text="")
            self.logo_label.pack(pady=(20, 0)) # Spacing at the top
        except Exception as e:
            print(f"DEBUG: Logo could not be loaded: {e}")
            # If the logo fails, the app will still run without crashing

        # --- REST OF HER ORIGINAL UI ---
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