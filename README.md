# Restaurant Billing and Management System

A robust, lightweight desktop Point-of-Sale (POS) and billing application built using **Python**, **Tkinter**, and **SQLite3**. Designed for small-to-medium restaurant setups, this system streamlines order processing, automated calculations (including GST), persistent database record-keeping, and zero-cost digital receipt sharing.

---

## 🚀 Key Features

* **Interactive GUI Dashboard:** Built using Python's native `Tkinter` and styled with `ttk` for a modern, responsive user experience.
* **Preset Food Menu & Dynamic Pricing:** Dropdown selection with auto-filling unit prices to minimize human entry errors.
* **Automated Calculations:** Instantly computes sub-totals, 5% GST computation, and grand totals.
* **Relational Database Storage:** Uses **SQLite3** (`restaurant_management.db`) to persistently log customer orders, item details, and transaction timestamps.
* **Saved Records View:** A dedicated tab featuring a scrollable `Treeview` table to audit and refresh historical sales transactions.
* **100% Free Digital Receipt Dispatches:**
  * **WhatsApp Web Integration:** Automatically formats and launches direct WhatsApp Web/Desktop links with pre-filled invoices (`urllib.parse` and `webbrowser`).
  * **Email Invoicing:** Transmits text-based professional invoices instantly via Gmail SMTP (`smtplib`).

---

## 🛠️ Tech Stack

* **Language:** Python 3.8+
* **GUI Framework:** Tkinter / ttk
* **Database:** SQLite3
* **Protocols & Integrations:** SMTP (Gmail TLS), WhatsApp Web API URL scheme

---

## ⚙️ Installation & Setup

1. **Clone or Download Repository:**
   ```bash
   git clone [https://github.com/antox5/hotel_bill_generator.git](https://github.com/antox5/hotel_bill_generator.git)
   cd hotel_bill_generator
