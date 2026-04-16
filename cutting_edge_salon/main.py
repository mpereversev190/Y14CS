import customtkinter as ctk
from database import Database

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

        self.current_user = None   # <-- store logged-in user

        self.title("Cutting Edge Hair Salon - Management System")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.db = Database()

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for ViewClass in (WelcomeView, LoginView, DashboardView, StaffView, CustomerView, BookingView, PaymentView):
            page_name = ViewClass.__name__
            frame = ViewClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_view("WelcomeView")

    def show_view(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()
        frame.tkraise()



    def has_role(self, *roles):
        if not self.current_user:
            return False

        # Convert Enum to string
        user_role = self.current_user.role.value  

        return user_role in roles


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
