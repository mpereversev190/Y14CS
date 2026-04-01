import customtkinter as ctk
from database import Database

# import all views from package
from views.welcome_view import WelcomeView
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.staff_view import StaffView
from views.customer_view import CustomerView
from views.booking_view import BookingView
from views.payment_view import PaymentView

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Cutting Edge Hair Salon - Management System")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # initialise database
        self.db = Database()

        # create main container - all views inside
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # view mapping
        # store classes in a dictionary for easy switching
        self.frames = {}
        for ViewClass in (WelcomeView, LoginView, DashboardView, StaffView, CustomerView, BookingView, PaymentView):
            page_name = ViewClass.__name__
            # create frame
            frame = ViewClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # show landing page
        self.show_view("WelcomeView")

    def show_view(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        
        # if the view has a refresh method (like staff/customer tables), call it
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()
            
        frame.tkraise()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

