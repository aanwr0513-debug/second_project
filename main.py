from tkinter import *
from tkinter import ttk, messagebox, filedialog
import database
import random
import os

# --- نافذة تسجيل الدخول ---
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Store Management System")
        self.root.geometry("400x300")
        self.root.config(bg="#2c3e50")
        self.root.resizable(False, False)

        self.username_var = StringVar()
        self.password_var = StringVar()

        frame = Frame(self.root, bg="white", bd=2, relief="groove")
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=340, height=240)

        Label(frame, text="System Login", font=("Tahoma", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=15)

        Label(frame, text="Username:", font=("Tahoma", 9, "bold"), bg="white").pack(anchor="w", padx=25)
        Entry(frame, textvariable=self.username_var, font=("Tahoma", 11), width=24, bd=2, relief="solid").pack(pady=5)

        Label(frame, text="Password:", font=("Tahoma", 9, "bold"), bg="white").pack(anchor="w", padx=25)
        Entry(frame, textvariable=self.password_var, show="*", font=("Tahoma", 11), width=24, bd=2, relief="solid").pack(pady=5)

        Button(frame, text="Login", font=("Tahoma", 10, "bold"), bg="#28a745", fg="white", width=20, bd=0, command=self.verify_login).pack(pady=15)

    def verify_login(self):
        uname = self.username_var.get().strip()
        upass = self.password_var.get().strip()

        if not uname or not upass:
            messagebox.showerror("Error", "Please enter username and password.")
            return

        role = database.check_user_login(uname, upass)
        if role:
            messagebox.showinfo("Success", f"Welcome ({uname})\nRole: {role}")
            self.root.destroy()
            open_main_app(role)
        else:
            messagebox.showerror("Failed", "Incorrect username or password!")


# --- التطبيق الرئيسي لنقطة البيع والإدارة ---
def open_main_app(user_role):
    app = Tk()
    app.title("Advanced Store Management & POS System")
    app.geometry("1200x740")
    app.config(bg="#f8f9fa")

    barcode_var = StringVar()
    name_var = StringVar()
    price_var = StringVar()
    qty_var = StringVar()
    search_var = StringVar()
    pos_barcode_var = StringVar()

    def load_data(data=None):
        for row in tree.get_children():
            tree.delete(row)
        
        rows = data if data is not None else database.get_all_products()
        total_inventory_value = 0
        
        for row in rows:
            p_id, barcode, name, price, qty = row
            total_inventory_value += (price * qty)
            tag = 'low_stock' if qty <= 3 else ''
            tree.insert("", END, values=row, tags=(tag,))
        
        lbl_total.config(text=f"Total Value: {total_inventory_value:.2f} LYD")

    def clear_entries():
        barcode_var.set("")
        name_var.set("")
        price_var.set("")
        qty_var.set("")
        pos_barcode_var.set("")
        search_var.set("")
        load_data()

    def get_row_data(event):
        selected_item = tree.focus()
        if not selected_item:
            return
        values = tree.item(selected_item, 'values')
        clear_entries()
        barcode_var.set(values[1])
        name_var.set(values[2])
        price_var.set(values[3])
        qty_var.set(values[4])

    def add_item():
        b_code = barcode_var.get().strip()
        p_name = name_var.get().strip()
        p_price = price_var.get().strip()
        p_qty = qty_var.get().strip()

        if not b_code or not p_name or not p_price or not p_qty:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            price = float(p_price)
            qty = int(p_qty)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and quantity an integer.")
            return

        success = database.add_product(b_code, p_name, price, qty)
        if success:
            messagebox.showinfo("Success", "Product added successfully.")
            clear_entries()
            load_data()
        else:
            messagebox.showerror("Error", "Barcode already exists!")

    def update_item():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product from the table.")
            return
        
        values = tree.item(selected_item, 'values')
        product_id = values[0]

        b_code = barcode_var.get().strip()
        p_name = name_var.get().strip()
        p_price = price_var.get().strip()
        p_qty = qty_var.get().strip()

        if not b_code or not p_name or not p_price or not p_qty:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            price = float(p_price)
            qty = int(p_qty)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values.")
            return

        database.update_product(product_id, b_code, p_name, price, qty)
        messagebox.showinfo("Success", "Product updated successfully.")
        clear_entries()
        load_data()

    def delete_item():
        if user_role != "مدير":
            messagebox.showerror("Access Denied", "Product deletion is restricted to Managers only!")
            return

        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
        
        values = tree.item(selected_item, 'values')
        product_id = values[0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            database.delete_product(product_id)
            clear_entries()
            load_data()
            messagebox.showinfo("Success", "Deleted successfully.")

    def search_item(event):
        term = search_var.get()
        results = database.search_products(term)
        load_data(results)

    def process_barcode_sale(event=None):
        b_code = pos_barcode_var.get().strip()
        if not b_code:
            return
        
        product = database.get_product_by_barcode(b_code)
        if product:
            p_id, _, p_name, p_price, p_qty = product
            if p_qty > 0:
                new_qty = p_qty - 1
                database.update_product(p_id, product[1], p_name, p_price, new_qty)
                
                invoice_no = f"INV-{random.randint(10000, 99999)}"
                database.record_sale(invoice_no, p_name, p_price, 1)
                
                load_data()
                pos_barcode_var.set("")
                
                # طباعة إيصال بيع حراري وهمي / ملف نصي
                receipt_text = f"""
=====================================
          STORE RECEIPT
=====================================
Invoice No: {invoice_no}
Item Name : {p_name}
Price     : {p_price} LYD
Qty       : 1
Total     : {p_price} LYD
-------------------------------------
Thank you for shopping with us!
=====================================
"""
                receipt_filename = f"{invoice_no}.txt"
                with open(receipt_filename, "w", encoding="utf-8") as f:
                    f.write(receipt_text)
                
                messagebox.showinfo("POS Sale", f"Sold: {p_name}\nPrice: {p_price} LYD\nInvoice: {invoice_no}\nReceipt saved as {receipt_filename}")
            else:
                messagebox.showwarning("Stock Alert", f"Sorry, item ({p_name}) is out of stock!")
        else:
            messagebox.showerror("Error", "Barcode not registered in the system!")
            pos_barcode_var.set("")

    def show_sales_report():
        report_win = Toplevel(app)
        report_win.title("Sales Reports & Invoices")
        report_win.geometry("850x480")
        report_win.config(bg="#f8f9fa")

        Label(report_win, text="📊 Sales & Invoices Records", font=("Tahoma", 13, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=10)

        rep_frame = Frame(report_win, bg="white")
        rep_frame.pack(fill="both", expand=True, padx=15, pady=5)

        scroll_r = Scrollbar(rep_frame, orient=VERTICAL)
        scroll_r.pack(side=RIGHT, fill=Y)

        rep_tree = ttk.Treeview(rep_frame, columns=("id", "inv", "name", "price", "qty", "total", "date"), show="headings", yscrollcommand=scroll_r.set)
        scroll_r.config(command=rep_tree.yview)

        rep_tree.heading("id", text="ID")
        rep_tree.heading("inv", text="Invoice No")
        rep_tree.heading("name", text="Item Name")
        rep_tree.heading("price", text="Price")
        rep_tree.heading("qty", text="Qty")
        rep_tree.heading("total", text="Total")
        rep_tree.heading("date", text="Date & Time")

        rep_tree.column("id", width=40, anchor=CENTER)
        rep_tree.column("inv", width=100, anchor=CENTER)
        rep_tree.column("name", width=180, anchor=CENTER)
        rep_tree.column("price", width=80, anchor=CENTER)
        rep_tree.column("qty", width=50, anchor=CENTER)
        rep_tree.column("total", width=90, anchor=CENTER)
        rep_tree.column("date", width=140, anchor=CENTER)

        rep_tree.pack(fill="both", expand=True)

        sales_data = database.get_all_sales()
        total_sales_revenue = 0
        for s in sales_data:
            total_sales_revenue += s[5]
            rep_tree.insert("", END, values=s)

        def export_to_csv():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8-sig") as f:
                        f.write("ID,Invoice No,Item Name,Price,Qty,Total,Date Time\n")
                        for s in sales_data:
                            f.write(f"{s[0]},{s[1]},{s[2]},{s[3]},{s[4]},{s[5]},{s[6]}\n")
                    messagebox.showinfo("Export", "Sales report exported to CSV successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export: {e}")

        bottom_rep_frame = Frame(report_win, bg="#f8f9fa")
        bottom_rep_frame.pack(fill="x", padx=15, pady=10)

        Label(bottom_rep_frame, text=f"Total Revenue: {total_sales_revenue:.2f} LYD", font=("Tahoma", 11, "bold"), bg="#f8f9fa", fg="#27ae60").pack(side=LEFT)
        Button(bottom_rep_frame, text="📥 Export to CSV", font=("Tahoma", 9, "bold"), bg="#17a2b8", fg="white", bd=0, padx=10, pady=5, command=export_to_csv).pack(side=RIGHT)

    def show_users_management():
        if user_role != "مدير":
            messagebox.showerror("Access Denied", "User management is restricted to Managers only!")
            return

        u_win = Toplevel(app)
        u_win.title("Users Management")
        u_win.geometry("450x400")
        u_win.config(bg="#f8f9fa")

        Label(u_win, text="👥 Manage System Users", font=("Tahoma", 12, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=10)

        add_u_frame = Frame(u_win, bg="#f8f9fa")
        add_u_frame.pack(fill="x", padx=20, pady=5)

        new_uname = StringVar()
        new_upass = StringVar()
        new_role = StringVar(value="كاشير")

        Label(add_u_frame, text="Username:", font=("Tahoma", 9), bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=2)
        Entry(add_u_frame, textvariable=new_uname, font=("Tahoma", 10), width=18).grid(row=0, column=1, pady=2)

        Label(add_u_frame, text="Password:", font=("Tahoma", 9), bg="#f8f9fa").grid(row=1, column=0, sticky="w", pady=2)
        Entry(add_u_frame, textvariable=new_upass, show="*", font=("Tahoma", 10), width=18).grid(row=1, column=1, pady=2)

        Label(add_u_frame, text="Role:", font=("Tahoma", 9), bg="#f8f9fa").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Combobox(add_u_frame, textvariable=new_role, values=["مدير", "كاشير"], state="readonly", width=16).grid(row=2, column=1, pady=2)

        def save_new_user():
            uname = new_uname.get().strip()
            upass = new_upass.get().strip()
            role = new_role.get().strip()
            if not uname or not upass:
                messagebox.showerror("Error", "Fill all user fields.")
                return
            success = database.add_user(uname, upass, role)
            if success:
                messagebox.showinfo("Success", "User added successfully.")
                refresh_users_table()
                new_uname.set("")
                new_upass.set("")
            else:
                messagebox.showerror("Error", "Username already exists!")

        Button(add_u_frame, text="Add User", font=("Tahoma", 9, "bold"), bg="#28a745", fg="white", bd=0, command=save_new_user).grid(row=3, column=0, columnspan=2, pady=8)

        users_table_frame = Frame(u_win, bg="white")
        users_table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        u_tree = ttk.Treeview(users_table_frame, columns=("id", "username", "role"), show="headings")
        u_tree.heading("id", text="ID")
        u_tree.heading("username", text="Username")
        u_tree.heading("role", text="Role")
        u_tree.column("id", width=50, anchor=CENTER)
        u_tree.column("username", width=180, anchor=CENTER)
        u_tree.column("role", width=120, anchor=CENTER)
        u_tree.pack(fill="both", expand=True)

        def refresh_users_table():
            for row in u_tree.get_children():
                u_tree.delete(row)
            for u in database.get_all_users():
                u_tree.insert("", END, values=u)

        refresh_users_table()

        def delete_selected_user():
            selected = u_tree.focus()
            if not selected:
                messagebox.showwarning("Warning", "Select a user to delete.")
                return
            vals = u_tree.item(selected, 'values')
            if vals[1] == 'admin':
                messagebox.showerror("Error", "Cannot delete main admin account!")
                return
            if messagebox.askyesno("Confirm", "Delete selected user?"):
                database.delete_user(vals[0])
                refresh_users_table()
                messagebox.showinfo("Success", "User deleted.")

        Button(u_win, text="Delete Selected User", font=("Tahoma", 9, "bold"), bg="#dc3545", fg="white", bd=0, command=delete_selected_user).pack(pady=5)

    def show_item_card():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to view its card.")
            return
        
        values = tree.item(selected_item, 'values')
        
        card_window = Toplevel(app)
        card_window.title("Item Barcode Card")
        card_window.geometry("420x340")
        card_window.config(bg="white")
        
        Label(card_window, text="Item Information Card", font=("Tahoma", 14, "bold"), bg="white", fg="#007bff").pack(pady=10)
        
        info_frame = Frame(card_window, bg="white")
        info_frame.pack(fill="x", padx=30, pady=8)
        
        Label(info_frame, text=f"Item Name: {values[2]}", font=("Tahoma", 11, "bold"), bg="white", anchor="w").pack(fill="x", pady=3)
        Label(info_frame, text=f"Price: {values[3]} LYD", font=("Tahoma", 10), bg="white", fg="#27ae60", anchor="w").pack(fill="x", pady=3)
        Label(info_frame, text=f"Stock Qty: {values[4]} pcs", font=("Tahoma", 10), bg="white", fg="#e67e22", anchor="w").pack(fill="x", pady=3)
        Label(card_window, text=f"Barcode: *{values[1]}*", font=("Consolas", 14, "bold"), bg="white", fg="#333").pack(pady=15)
        
        Button(card_window, text="Print Card", font=("Tahoma", 10, "bold"), bg="#007bff", fg="white", bd=0, padx=15, pady=5, command=lambda: messagebox.showinfo("Print", "Barcode card sent to printer successfully!")).pack(pady=10)

    header_frame = Frame(app, bg="#2c3e50", height=65)
    header_frame.pack(fill="x")
    Label(header_frame, text="🛒 Advanced Store Management & POS", font=("Tahoma", 15, "bold"), bg="#2c3e50", fg="white").pack(side=LEFT, padx=20)
    Label(header_frame, text=f"User: ({user_role}) | Dev: Alzool", font=("Tahoma", 10, "bold"), bg="#2c3e50", fg="#f39c12").pack(side=RIGHT, padx=20)

    main_container = Frame(app, bg="#f8f9fa")
    main_container.pack(fill="both", expand=True, padx=15, pady=15)

    lf_manage = LabelFrame(main_container, text=" Product & Barcode Management ", font=("Tahoma", 11, "bold"), bg="#f8f9fa")
    lf_manage.pack(fill="x", pady=(0, 10))

    Label(lf_manage, text="Item Name:", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=0, column=3, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=name_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=0, column=2, padx=5, pady=8)

    Label(lf_manage, text="Barcode:", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=0, column=1, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=barcode_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=0, column=0, padx=5, pady=8)

    Label(lf_manage, text="Price (LYD):", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=1, column=3, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=price_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=1, column=2, padx=5, pady=8)

    Label(lf_manage, text="Quantity:", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=1, column=1, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=qty_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=1, column=0, padx=5, pady=8)

    control_frame = Frame(main_container, bg="#f8f9fa")
    control_frame.pack(fill="x", pady=5)

    lf_pos = LabelFrame(control_frame, text="⚡ Fast POS", font=("Tahoma", 10, "bold"), bg="#e8f4f8")
    lf_pos.pack(side=LEFT, fill="x", expand=True, padx=(0, 5))
    Label(lf_pos, text="Scan Barcode:", font=("Tahoma", 9, "bold"), bg="#e8f4f8").pack(side=LEFT, padx=5)
    pos_entry = Entry(lf_pos, textvariable=pos_barcode_var, font=("Tahoma", 11), width=14, bd=2, relief="groove")
    pos_entry.pack(side=LEFT, padx=5)
    pos_entry.bind("<Return>", process_barcode_sale)
    Button(lf_pos, text="Sell", font=("Tahoma", 9, "bold"), bg="#17a2b8", fg="white", bd=0, padx=10, command=process_barcode_sale).pack(side=LEFT, padx=5)

    lf_search = LabelFrame(control_frame, text="🔍 Product Search", font=("Tahoma", 10, "bold"), bg="#f8f9fa")
    lf_search.pack(side=RIGHT, fill="x", expand=True, padx=(5, 0))
    Label(lf_search, text="Search:", font=("Tahoma", 9), bg="#f8f9fa").pack(side=LEFT, padx=5)
    search_entry = Entry(lf_search, textvariable=search_var, font=("Tahoma", 11), width=14, bd=2, relief="groove")
    search_entry.pack(side=LEFT, padx=5)
    search_entry.bind("<KeyRelease>", search_item)

    btns_frame = Frame(main_container, bg="#f8f9fa", pady=10)
    btns_frame.pack(fill="x")

    Button(btns_frame, text="➕ Add", font=("Tahoma", 9, "bold"), bg="#28a745", fg="white", bd=0, padx=6, pady=5, command=add_item).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="✏️ Update", font=("Tahoma", 9, "bold"), bg="#ffc107", fg="#333", bd=0, padx=6, pady=5, command=update_item).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="🗑️ Delete", font=("Tahoma", 9, "bold"), bg="#dc3545", fg="white", bd=0, padx=6, pady=5, command=delete_item).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="📊 Reports", font=("Tahoma", 9, "bold"), bg="#6f42c1", fg="white", bd=0, padx=6, pady=5, command=show_sales_report).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="👥 Users", font=("Tahoma", 9, "bold"), bg="#fd7e14", fg="white", bd=0, padx=6, pady=5, command=show_users_management).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="🏷️ Card", font=("Tahoma", 9, "bold"), bg="#007bff", fg="white", bd=0, padx=6, pady=5, command=show_item_card).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="🧹 Clear", font=("Tahoma", 9, "bold"), bg="#6c757d", fg="white", bd=0, padx=6, pady=5, command=clear_entries).pack(side=LEFT, expand=True, padx=2)

    table_frame = Frame(main_container, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True, pady=5)

    scroll_y = Scrollbar(table_frame, orient=VERTICAL)
    scroll_y.pack(side=RIGHT, fill=Y)

    tree = ttk.Treeview(table_frame, columns=("id", "barcode", "name", "price", "qty"), show="headings", yscrollcommand=scroll_y.set)
    scroll_y.config(command=tree.yview)

    tree.heading("id", text="ID")
    tree.heading("barcode", text="Barcode")
    tree.heading("name", text="Item Name")
    tree.heading("price", text="Price (LYD)")
    tree.heading("qty", text="Available Qty")

    tree.column("id", width=60, anchor=CENTER)
    tree.column("barcode", width=160, anchor=CENTER)
    tree.column("name", width=250, anchor=CENTER)
    tree.column("price", width=120, anchor=CENTER)
    tree.column("qty", width=120, anchor=CENTER)

    tree.pack(fill="both", expand=True)
    tree.bind("<ButtonRelease-1>", get_row_data)
    tree.tag_configure('low_stock', background='#f8d7da')

    footer_frame = Frame(app, bg="#343a40", height=45)
    footer_frame.pack(fill="x", side=BOTTOM)

    lbl_total = Label(footer_frame, text="Total Value: 0.00 LYD", font=("Tahoma", 10, "bold"), bg="#343a40", fg="white")
    lbl_total.pack(side=RIGHT, padx=20, pady=10)
    Label(footer_frame, text="Developer: Alzool", font=("Tahoma", 9, "bold"), bg="#343a40", fg="#f39c12").pack(side=LEFT, padx=20, pady=10)

    load_data()
    app.mainloop()

if __name__ == "__main__":
    root = Tk()
    LoginWindow(root)
    root.mainloop()
