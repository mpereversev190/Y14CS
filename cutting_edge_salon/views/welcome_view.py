import customtkinter as ctk
import os
from PIL import Image

class WelcomeView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # load logo
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(base_dir, "assets", "logo.png") #looks in folder of system 

            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(250, 250)  # slightly larger for the welcome screen
            )

            self.logo_label = ctk.CTkLabel(self, image=self.logo_img, text="")
            self.logo_label.pack(pady=(30, 10))
        except Exception as e:
            print(f"DEBUG: Welcome logo error: {e}")

        # GUI
        self.label = ctk.CTkLabel(
            self, 
            text="Cutting Edge Salon", 
            font=("Helvetica", 32, "bold")
        )
        self.label.pack(pady=20)

        self.subtitle = ctk.CTkLabel(
            self, 
            text="Premium Styling & Care", 
            font=("Helvetica", 16, "italic")
        )
        self.subtitle.pack(pady=(0, 40))

        # navigation
        self.login_btn = ctk.CTkButton(
            self, 
            text="Staff Login", 
            width=200,
            height=40,
            command=lambda: controller.show_view("LoginView")
        )
        self.login_btn.pack(pady=10)

        self.exit_btn = ctk.CTkButton(
            self, 
            text="Exit System", 
            fg_color="transparent", 
            border_width=1,
            width=200,
            command=self.quit
        )
        self.exit_btn.pack(pady=10)