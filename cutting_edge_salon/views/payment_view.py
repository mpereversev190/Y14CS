import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime

class PaymentView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        
        super().__init__(parent)
        self.controller = controller
                # access check to make sure user has admin role
        if not self.controller.has_role("admin"):
            messagebox.showerror("Access Denied", "Only admins can access Payment Management.")
            self.controller.show_view("DashboardView")
            return
        self.selected_payment_id = None

        ctk.CTkLabel(self, text="Payment Management", font=("Helvetica", 20, "bold")).pack(pady=10)

        # search bar
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=20, pady=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by customer name...")
        self.search_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        ctk.CTkButton(search_frame, text="Search", width=100, command=self.refresh_payments).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Clear", width=100, fg_color="gray", command=self.clear_search).pack(side="left", padx=5)

        # load appointments
        self.appointments = self.controller.db.fetch_appointments_with_prices()

        appointment_labels = []
        self.appointment_map = {}  # label  appointment_id

        for appt in self.appointments:
            appt_id, dt, customer, service, price = appt
            label = f"#{appt_id} – {dt} – {customer} – {service}"
            appointment_labels.append(label)
            self.appointment_map[label] = appt

        # input form
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=20, pady=10)

        self.appointment_var = ctk.StringVar()
        self.customer_var = ctk.StringVar()
        self.service_var = ctk.StringVar()
        self.amount_var = ctk.StringVar()
        self.method_var = ctk.StringVar(value="Cash")
        self.status_var = ctk.StringVar(value="pending")

        # appointment dropdown
        ctk.CTkOptionMenu(form_frame, values=appointment_labels, variable=self.appointment_var,
                          command=self.on_appointment_selected).grid(row=0, column=0, padx=10, pady=10)

        # read-only customer + service
        ctk.CTkEntry(form_frame, textvariable=self.customer_var, state="readonly").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkEntry(form_frame, textvariable=self.service_var, state="readonly").grid(row=0, column=2, padx=10, pady=10)

        # amount entry
        ctk.CTkEntry(form_frame, placeholder_text="Amount (£)", textvariable=self.amount_var).grid(row=1, column=0, padx=10, pady=10)

        # payment method
        ctk.CTkOptionMenu(form_frame, values=["Cash", "Card"], variable=self.method_var,
                          command=lambda _: self.toggle_card_details()).grid(row=1, column=1, padx=10, pady=10)

        # status
        ctk.CTkOptionMenu(form_frame, values=["pending", "paid", "refunded"], variable=self.status_var).grid(row=1, column=2, padx=10, pady=10)

        # card details (only show if card selected)
        self.card_frame = ctk.CTkFrame(self)
        self.card_frame.pack(fill="x", padx=20, pady=5)
        self.card_frame.pack_forget()  # hidden by default

        self.card_number_var = ctk.StringVar()
        self.card_expiry_var = ctk.StringVar()
        self.card_holder_var = ctk.StringVar()

        ctk.CTkEntry(self.card_frame, placeholder_text="Card Number (16 digits)",
                     textvariable=self.card_number_var).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkEntry(self.card_frame, placeholder_text="Expiry (MM/YY)",
                     textvariable=self.card_expiry_var).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkEntry(self.card_frame, placeholder_text="Card Holder",
                     textvariable=self.card_holder_var).grid(row=0, column=2, padx=10, pady=5)

        # action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        ctk.CTkButton(btn_frame, text="Add Payment", fg_color="green", command=self.add_payment).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Update Selected", command=self.update_payment).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="red", command=self.delete_payment).pack(side="left", padx=5)

        # payments button
        self.tree = ttk.Treeview(
            self,
            columns=("ID", "ApptID", "Customer", "Amount", "Method", "Status", "Date"),
            show="headings"
        )

        for col in ("ID", "ApptID", "Customer", "Amount", "Method", "Status", "Date"):
            self.tree.heading(col, text=col)

        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        ctk.CTkButton(self, text="Back to Dashboard",
                      command=lambda: self.controller.show_view("DashboardView")).pack(pady=10)

        self.refresh_payments()

    # logic

    def on_appointment_selected(self, label):
        appt_id, dt, customer, service, price = self.appointment_map[label]

        self.customer_var.set(customer)
        self.service_var.set(service)

        # auto-fill amount with the service price
        self.amount_var.set(str(price))


    def toggle_card_details(self):
        if self.method_var.get() == "Card":
            self.card_frame.pack(fill="x", padx=20, pady=5)
        else:
            self.card_frame.pack_forget()

    def refresh_payments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_entry.get()
        records = self.controller.db.fetch_all_payments(search)

        for r in records:
            self.tree.insert("", "end", values=r)

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.refresh_payments()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected)['values']
        self.selected_payment_id = values[0]

        # load payment details
        details = self.controller.db.fetch_payment_details(self.selected_payment_id)
        if not details:
            return

        (pid, customer, service, amount, date, method, last4, expiry, holder) = details

        self.amount_var.set(amount)
        self.method_var.set(method)
        self.status_var.set(values[5])

        if method == "Card":
            self.toggle_card_details()
            self.card_number_var.set("**** **** **** " + (last4 or ""))
            self.card_expiry_var.set(expiry or "")
            self.card_holder_var.set(holder or "")
        else:
            self.toggle_card_details()

    def add_payment(self):
        if not self.appointment_var.get():
            messagebox.showwarning("Missing", "Select an appointment first")
            return

        appt_id = self.appointment_map[self.appointment_var.get()][0]

        try:
            amount = float(self.amount_var.get())
        except:
            messagebox.showwarning("Invalid", "Amount must be a number")
            return

        method = self.method_var.get()
        status = self.status_var.get()

        card_last4 = None
        card_expiry = None
        card_holder = None

        if method == "Card":
            num = ''.join(filter(str.isdigit, self.card_number_var.get()))
            if len(num) != 16:
                messagebox.showwarning("Invalid", "Card number must be 16 digits")
                return
            card_last4 = num[-4:]
            card_expiry = self.card_expiry_var.get()
            card_holder = self.card_holder_var.get()

        self.controller.db.insert_payment(
            appt_id, amount, method, status,
            card_last4, card_expiry, card_holder
        )

        self.refresh_payments()
        messagebox.showinfo("Success", "Payment added")

    def update_payment(self):
        if not self.selected_payment_id:
            messagebox.showwarning("Select", "Select a payment to update")
            return

        method = self.method_var.get()
        status = self.status_var.get()

        card_last4 = None
        card_expiry = None
        card_holder = None

        if method == "Card":
            num = ''.join(filter(str.isdigit, self.card_number_var.get()))
            if len(num) != 16:
                messagebox.showwarning("Invalid", "Card number must be 16 digits")
                return
            card_last4 = num[-4:]
            card_expiry = self.card_expiry_var.get()
            card_holder = self.card_holder_var.get()

        self.controller.db.update_payment(
            self.selected_payment_id,
            method, status,
            card_last4, card_expiry, card_holder
        )

        self.refresh_payments()
        messagebox.showinfo("Updated", "Payment updated")

    def delete_payment(self):
        if not self.selected_payment_id:
            return

        if messagebox.askyesno("Confirm", "Delete this payment?"):
            self.controller.db.delete_payment(self.selected_payment_id)
            self.refresh_payments()
