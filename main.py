import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

# ==========================================
# 1. PRESET FOOD MENU & PRICING
# ==========================================
FOOD_MENU = {
    "Dosa": 50.00,
    "Idly (2 Pcs)": 30.00,
    "Biriyani": 180.00,
    "Chappathi (2 Pcs)": 40.00,
    "Parotta (2 Pcs)": 45.00,
    "Full Meals": 120.00,
}

# ==========================================
# 2. DATABASE INITIALIZATION (SQLite3)
# ==========================================
def init_db():
    conn = sqlite3.connect("restaurant_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            sub_total REAL NOT NULL,
            gst REAL NOT NULL,
            grand_total REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. GUI APPLICATION CLASS
# ==========================================
class RestaurantBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Billing & Management System")
        self.root.geometry("850x550")
        self.root.configure(bg="#FFF8F0")

        # Color Palette
        self.ORANGE = "#FF6F00"
        self.WHITE = "#FFFFFF"
        self.LIGHT_ORANGE = "#FFE0B2"
        self.TEXT_COLOR = "#212121"
        self.WA_GREEN = "#25D366"

        # Apply ttk Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TNotebook", background=self.WHITE, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=self.LIGHT_ORANGE,
            foreground=self.TEXT_COLOR,
            font=("Helvetica", 10, "bold"),
            padding=[12, 6]
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.ORANGE)],
            foreground=[("selected", self.WHITE)]
        )

        self.style.configure("Treeview", rowheight=25, font=("Helvetica", 9), background=self.WHITE)
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background=self.ORANGE, foreground=self.WHITE)

        # Header Banner
        title_label = tk.Label(
            self.root,
            text="RESTAURANT BILLING SYSTEM",
            font=("Helvetica", 16, "bold"),
            bg=self.ORANGE,
            fg=self.WHITE,
            pady=10
        )
        title_label.pack(fill=tk.X)

        # Tabs Layout
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.billing_tab = tk.Frame(self.notebook, bg=self.WHITE)
        self.records_tab = tk.Frame(self.notebook, bg=self.WHITE)

        self.notebook.add(self.billing_tab, text=" New Order & Billing ")
        self.notebook.add(self.records_tab, text=" View Saved Records ")

        self.build_billing_ui()
        self.build_records_ui()

    # ------------------------------------------
    # 3.1 BILLING TAB INTERFACE
    # ------------------------------------------
    def build_billing_ui(self):
        # Customer Details Frame
        cust_frame = tk.LabelFrame(
            self.billing_tab, text=" Customer Information ",
            font=("Helvetica", 11, "bold"), bg=self.WHITE, fg=self.ORANGE, padx=10, pady=10
        )
        cust_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(cust_frame, text="Name:", bg=self.WHITE, font=("Helvetica", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cust_name = tk.Entry(cust_frame, font=("Helvetica", 10), width=20, relief=tk.SOLID, bd=1)
        self.cust_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(cust_frame, text="Phone (10 digits):", bg=self.WHITE, font=("Helvetica", 10)).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.cust_phone = tk.Entry(cust_frame, font=("Helvetica", 10), width=20, relief=tk.SOLID, bd=1)
        self.cust_phone.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(cust_frame, text="Email:", bg=self.WHITE, font=("Helvetica", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cust_email = tk.Entry(cust_frame, font=("Helvetica", 10), width=20, relief=tk.SOLID, bd=1)
        self.cust_email.grid(row=1, column=1, padx=5, pady=5)

        # Order Details Frame
        order_frame = tk.LabelFrame(
            self.billing_tab, text=" Order Details ",
            font=("Helvetica", 11, "bold"), bg=self.WHITE, fg=self.ORANGE, padx=10, pady=10
        )
        order_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(order_frame, text="Select Food Item:", bg=self.WHITE, font=("Helvetica", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.food_cb = ttk.Combobox(order_frame, values=list(FOOD_MENU.keys()), state="readonly", width=20)
        self.food_cb.current(0)
        self.food_cb.grid(row=0, column=1, padx=5, pady=5)
        self.food_cb.bind("<<ComboboxSelected>>", self.auto_update_price)

        tk.Label(order_frame, text="Unit Price (₹):", bg=self.WHITE, font=("Helvetica", 10)).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.price_entry = tk.Entry(order_frame, font=("Helvetica", 10), width=15, relief=tk.SOLID, bd=1, state="readonly")
        self.price_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(order_frame, text="Quantity:", bg=self.WHITE, font=("Helvetica", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.qty_entry = tk.Entry(order_frame, font=("Helvetica", 10), width=22, relief=tk.SOLID, bd=1)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5)

        self.total_lbl = tk.Label(order_frame, text="Total: ₹0.00", font=("Helvetica", 11, "bold"), bg=self.WHITE, fg=self.ORANGE)
        self.total_lbl.grid(row=1, column=2, columnspan=2, sticky=tk.E, padx=5)

        self.auto_update_price()

        # Action Buttons
        btn_frame = tk.Frame(self.billing_tab, bg=self.WHITE)
        btn_frame.pack(fill=tk.X, padx=15, pady=20)

        btn_calc = tk.Button(
            btn_frame, text="Calculate Total", font=("Helvetica", 10, "bold"),
            bg=self.LIGHT_ORANGE, fg=self.ORANGE, cursor="hand2", bd=0, padx=12, pady=6,
            command=self.calculate_bill
        )
        btn_calc.pack(side=tk.LEFT, padx=5)

        btn_save = tk.Button(
            btn_frame, text="Save Order", font=("Helvetica", 10, "bold"),
            bg=self.ORANGE, fg=self.WHITE, cursor="hand2", bd=0, padx=12, pady=6,
            command=self.save_order
        )
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_email = tk.Button(
            btn_frame, text="Send Email", font=("Helvetica", 10, "bold"),
            bg="#E65100", fg=self.WHITE, cursor="hand2", bd=0, padx=12, pady=6,
            command=self.send_email
        )
        btn_email.pack(side=tk.LEFT, padx=5)

        btn_whatsapp = tk.Button(
            btn_frame, text="Send WhatsApp", font=("Helvetica", 10, "bold"),
            bg=self.WA_GREEN, fg=self.WHITE, activebackground="#1EBE5D", activeforeground=self.WHITE,
            cursor="hand2", bd=0, padx=12, pady=6,
            command=self.send_whatsapp_direct
        )
        btn_whatsapp.pack(side=tk.RIGHT, padx=5)

        self.order_data = None

    def auto_update_price(self, event=None):
        selected_item = self.food_cb.get()
        price = FOOD_MENU.get(selected_item, 0.0)

        self.price_entry.config(state="normal")
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, f"{price:.2f}")
        self.price_entry.config(state="readonly")

    # ------------------------------------------
    # 3.2 BILLING & TAX CALCULATION LOGIC
    # ------------------------------------------
    def calculate_bill(self):
        try:
            name = self.cust_name.get().strip()
            item = self.food_cb.get()
            price = FOOD_MENU[item]
            qty = int(self.qty_entry.get().strip())

            if not name:
                messagebox.showwarning("Input Error", "Please enter customer name.")
                return

            sub_total = price * qty
            gst = sub_total * 0.05
            grand_total = sub_total + gst

            self.order_data = {
                "name": name,
                "phone": self.cust_phone.get().strip(),
                "email": self.cust_email.get().strip(),
                "item": item,
                "price": price,
                "qty": qty,
                "sub_total": sub_total,
                "gst": gst,
                "grand_total": grand_total
            }

            self.total_lbl.config(text=f"Total: ₹{grand_total:.2f}")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric quantity.")

    # ------------------------------------------
    # 3.3 DATABASE TRANSACTION (INSERT)
    # ------------------------------------------
    def save_order(self):
        if not self.order_data:
            messagebox.showwarning("Warning", "Please calculate the bill first.")
            return

        try:
            conn = sqlite3.connect("restaurant_management.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (customer_name, phone, email, item_name, quantity, unit_price, sub_total, gst, grand_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.order_data["name"],
                self.order_data["phone"],
                self.order_data["email"],
                self.order_data["item"],
                self.order_data["qty"],
                self.order_data["price"],
                self.order_data["sub_total"],
                self.order_data["gst"],
                self.order_data["grand_total"]
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Order saved to database successfully!")
            self.load_records()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save order: {str(e)}")

    # ------------------------------------------
    # 3.4 EMAIL RECEIPT DISPATCH (SMTP)
    # ------------------------------------------
    def send_email(self):
        if not self.order_data or not self.order_data["email"]:
            messagebox.showwarning("Warning", "Calculated bill and valid email address required.")
            return

        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = self.order_data["email"]
        msg['Subject'] = "Your Restaurant Order Invoice"

        body = (
            f"Dear {self.order_data['name']},\n\n"
            f"Thank you for dining with us!\n\n"
            f"Item: {self.order_data['item']} (x{self.order_data['qty']})\n"
            f"Subtotal: ₹{self.order_data['sub_total']:.2f}\n"
            f"GST (5%): ₹{self.order_data['gst']:.2f}\n"
            f"Total Amount: ₹{self.order_data['grand_total']:.2f}\n\n"
            f"Have a great day!"
        )
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            messagebox.showinfo("Success", "Receipt emailed successfully!")
        except Exception as e:
            messagebox.showerror("Email Error", f"Error: {str(e)}")

    # ------------------------------------------
    # 3.5 WHATSAPP DIRECT DISPATCH
    # ------------------------------------------
    def send_whatsapp_direct(self):
        if not self.order_data or not self.order_data["phone"]:
            messagebox.showwarning("Warning", "Valid bill and phone number are required.")
            return

        phone_no = self.order_data["phone"].strip().replace(" ", "").replace("-", "")

        if not phone_no.startswith("+"):
            phone_no = "+91" + phone_no

        message = (
            f"Hello *{self.order_data['name']}*,\n\n"
            f"Thank you for dining with us!\n\n"
            f"*Order Details:*\n"
            f"• Item: {self.order_data['item']} (x{self.order_data['qty']})\n"
            f"• Subtotal: ₹{self.order_data['sub_total']:.2f}\n"
            f"• GST (5%): ₹{self.order_data['gst']:.2f}\n"
            f"• *Grand Total: ₹{self.order_data['grand_total']:.2f}*\n\n"
            f"Have a delicious day!"
        )

        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={phone_no}&text={encoded_message}"
        webbrowser.open(whatsapp_url)

    # ------------------------------------------
    # 3.6 RECORDS TAB INTERFACE & QUERY EXECUTION
    # ------------------------------------------
    def build_records_ui(self):
        top_frame = tk.Frame(self.records_tab, bg=self.WHITE)
        top_frame.pack(fill=tk.X, padx=15, pady=10)

        btn_refresh = tk.Button(
            top_frame, text="Refresh Table", font=("Helvetica", 10, "bold"),
            bg=self.ORANGE, fg=self.WHITE, cursor="hand2", bd=0, padx=10, pady=4,
            command=self.load_records
        )
        btn_refresh.pack(side=tk.LEFT)

        columns = ("ID", "Customer", "Phone", "Item", "Qty", "Price (₹)", "Total (₹)", "Date")
        self.tree = ttk.Treeview(self.records_tab, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=95)

        scrollbar = ttk.Scrollbar(self.records_tab, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=10)

        self.load_records()

    def load_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("restaurant_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_id, customer_name, phone, item_name, quantity, unit_price, grand_total, order_date 
            FROM orders ORDER BY order_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

# ==========================================
# 4. APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantBillingApp(root)
    root.mainloop()