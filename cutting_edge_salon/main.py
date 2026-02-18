import customtkinter as ctk
from database import Database

# Import all your views from the views package
from views.welcome_view import WelcomeView
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.staff_view import StaffView
from views.customer_view import CustomerView

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Configuration
        self.title("Cutting Edge Hair Salon - Management System")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 2. Initialize Database (Logic Layer)
        # This one instance is shared across all frames (Dependency Injection)
        self.db = Database()

        # 3. Create the Main Container
        # All views will be placed inside this frame
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 4. View Mapping
        # We store the classes in a dictionary for easy switching
        self.frames = {}
        for ViewClass in (WelcomeView, LoginView, DashboardView, StaffView, CustomerView):
            page_name = ViewClass.__name__
            # Create the frame but don't show it yet
            frame = ViewClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # 5. Show the landing page
        self.show_view("WelcomeView")

    def show_view(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        
        # If the view has a refresh method (like staff/customer tables), call it
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()
            
        frame.tkraise()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()