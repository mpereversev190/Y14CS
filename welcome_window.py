import tkinter
import customtkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import subprocess

class MainMenu(tk.CTk):
    def __init__(self):
        super().__init__()

        tk.set_appearance_mode("system") #sync with system light/dark mode
        tk.set_default_color_theme("dark-blue")


    
        self.title("Cutting Edge Main Menu")
        self.geometry("500x400")
        
        # configure grid layout, create title, logo and buttons
        self.configure_grid()
        self.create_title_label()
        self.create_logo()
        self.create_buttons_frame()

    
    def configure_grid(self):
        """Configure the grid layout for the main window"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def create_title_label(self):
        """Create the title label for the application"""
        self.title_label = tk.CTkLabel(
            self,
            text="Main Menu",
            font=tk.CTkFont(size=22, weight="bold", family="Helvetica"),
            text_color="white" 
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        #logo
    def create_logo(self):
        try:
            image = Image.open("logo.png")
            resized_image = image.resize((150, 150))
            self.logo_image = ImageTk.PhotoImage(resized_image)
            self.logo_label = tk.CTkLabel(self, image=self.logo_image, text="")
            self.logo_label.grid(row=1, column=0, pady=10)
        except FileNotFoundError:
            tk.Label(text="Logo not found (logo.png)").pack()
    def create_buttons_frame(self):
        """create buttons for system (features requested by client, check cw)"""
        self.buttons_frame = tk.CTkFrame(self, corner_radius=15, fg_color="#F8F8FF")
        self.buttons_frame.grid(row=2, column=0, padx=40, pady=20, sticky="nsew")
        
        # Configure buttons frame grid
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        
        # system features
        buttons = [
            ("Book a Slot", self.bookings),
            ("Staff Login", self.staff_login),
        ]
        for i, (button_text, command) in enumerate(buttons):
            btn = tk.CTkButton(
                self.buttons_frame,
                text=button_text,
                command=command,
                height=45,
                font=tk.CTkFont(size=15),
                corner_radius=8
            )
            btn.grid(row=i, column=0, padx=20, pady=8, sticky="ew")

    
    # Button handler functions

    def bookings(self):
        """Handle  booking functionality"""
        print("Book a Slot clicked!")
        # uncomment when file made
        # subprocess.Popen(['python3', 'file_name.py'])
        # self.destroy()


    def staff_login(self):
        """Handle staff login functionality"""
        print("Staff Login clicked!")
        #create the login window
        subprocess.Popen(['python3', 'staff_login.py'])
        self.destroy()


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()