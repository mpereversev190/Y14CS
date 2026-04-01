import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime

class BookingView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_appointment_id = None

        ctk.CTkLabel(self, text="Appointment Management", font=("Helvetica", 20, "bold")).pack(pady=10)

        # ---------------- SEARCH BAR ---------------- #
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=20, pady=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by customer name...")
        self.search_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        ctk.CTkButton(search_frame, text="Search", width=100, command=self.refresh_data).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Clear", width=100, fg_color="gray", command=self.clear_search).pack(side="left", padx=5)

        # ---------------- LOAD DROPDOWN DATA ---------------- #
        self.customers = self.controller.db.fetch_customers()
        self.stylists = self.controller.db.fetch_stylists()
        self.services = self.controller.db.fetch_services()

        customer_names = [c[1] for c in self.customers]
        stylist_names = [s[1] for s in self.stylists]
        service_names = [s[1] for s in self.services]

        # ---------------- INPUT FORM ---------------- #
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        self.datetime_var = ctk.StringVar(value="")

        ctk.CTkEntry(
            form_frame,
            placeholder_text="YYYY-MM-DD HH:MM",
            textvariable=self.datetime_var
        ).grid(row=0, column=0, padx=10, pady=10)


        self.notes_var = ctk.StringVar(value="")
        self.status_var = ctk.StringVar(value="Booked")
        self.customer_var = ctk.StringVar(value=customer_names[0] if customer_names else "")
        self.stylist_var = ctk.StringVar(value=stylist_names[0] if stylist_names else "")
        self.service_var = ctk.StringVar(value=service_names[0] if service_names else "")

        ctk.CTkEntry(form_frame, placeholder_text="Notes", textvariable=self.notes_var).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkOptionMenu(form_frame, values=["Booked", "Completed", "Cancelled", "No-Show"], variable=self.status_var).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkOptionMenu(form_frame, values=customer_names, variable=self.customer_var).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkOptionMenu(form_frame, values=stylist_names, variable=self.stylist_var).grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkOptionMenu(form_frame, values=service_names, variable=self.service_var).grid(row=1, column=2, padx=10, pady=10)

        # ---------------- ACTION BUTTONS ---------------- #
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        ctk.CTkButton(btn_frame, text="Add Appointment", fg_color="green", command=self.add_appointment).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Update Selected", command=self.update_appointment).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="red", command=self.delete_appointment).pack(side="left", padx=5)

        # ---------------- TABLE ---------------- #
        self.tree = ttk.Treeview(self, columns=("ID", "Date / Time", "Notes", "Status", "Customer", "Stylist", "Service"), show="headings")
        for col in ("ID", "Date / Time", "Notes", "Status", "Customer", "Stylist", "Service"):
            self.tree.heading(col, text=col)

        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        ctk.CTkButton(self, text="Back to Dashboard", command=lambda: self.controller.show_view("DashboardView")).pack(pady=10)

        self.refresh_data()

    # ---------------- VALIDATION ---------------- #
    def validate_inputs(self):
        return True

    # ---------------- DATA METHODS ---------------- #
    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_entry.get()
        records = self.controller.db.fetch_all_appointments(search_term)

        for r in records:
            self.tree.insert("", "end", values=r)

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.refresh_data()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        values = self.tree.item(selected_item)['values']
        self.selected_appointment_id = values[0]

        self.datetime_var.set(values[1])
        self.notes_var.set(values[2])
        self.status_var.set(values[3])
        self.customer_var.set(values[4])
        self.stylist_var.set(values[5])
        self.service_var.set(values[6])

    def add_appointment(self):
        # Auto-fill datetime if empty
        if not self.datetime_var.get().strip():
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.datetime_var.set(now)

        appointment_dt = self.datetime_var.get()
        print("DEBUG datetime:", appointment_dt)

        customer_id = next(c[0] for c in self.customers if c[1] == self.customer_var.get())
        stylist_id = next(s[0] for s in self.stylists if s[1] == self.stylist_var.get())
        service_id = next(s[0] for s in self.services if s[1] == self.service_var.get())

        try:
            self.controller.db.cur.execute("""
                INSERT INTO appointments (customer_id, stylist_id, service_id, appointment_datetime, notes, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (customer_id, stylist_id, service_id, appointment_dt, self.notes_var.get(), self.status_var.get()))

            self.controller.db.conn.commit()
            self.refresh_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add appointment: {e}")

    def update_appointment(self):
        if not self.selected_appointment_id:
            messagebox.showwarning("Selection", "Please select an appointment to update")
            return

        customer_id = next(c[0] for c in self.customers if c[1] == self.customer_var.get())
        stylist_id = next(s[0] for s in self.stylists if s[1] == self.stylist_var.get())
        service_id = next(s[0] for s in self.services if s[1] == self.service_var.get())

        try:
            self.controller.db.cur.execute("""
                UPDATE appointments
                SET customer_id=?, stylist_id=?, service_id=?, appointment_datetime=?, notes=?, status=?
                WHERE appointment_id=?
            """, (customer_id, stylist_id, service_id, self.datetime_var.get(), self.notes_var.get(),
                  self.status_var.get(), self.selected_appointment_id))

            self.controller.db.conn.commit()
            self.refresh_data()
            messagebox.showinfo("Success", "Appointment updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_appointment(self):
        if not self.selected_appointment_id:
            return

        if messagebox.askyesno("Confirm", "Delete this appointment?"):
            self.controller.db.delete_appointment(self.selected_appointment_id)
            self.refresh_data()
            self.clear_fields()

    def clear_fields(self):
        self.selected_appointment_id = None
        self.datetime_var.set("")
        self.notes_var.set("")
        self.status_var.set("Booked")
        self.customer_var.set("")
        self.stylist_var.set("")
        self.service_var.set("")
