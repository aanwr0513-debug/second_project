from tkinter import *
from tkinter import ttk, messagebox
import database
import random

# --- نافذة تسجيل الدخول ---
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("تسجيل الدخول - منظومة إدارة المحلات")
        self.root.geometry("400x300")
        self.root.config(bg="#2c3e50")
        self.root.resizable(False, False)

        self.username_var = StringVar()
        self.password_var = StringVar()

        frame = Frame(self.root, bg="white", bd=2, relief="groove")
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=340, height=240)

        Label(frame, text="تسجيل الدخول للمنظومة", font=("Tahoma", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=15)

        Label(frame, text="اسم المستخدم:", font=("Tahoma", 9, "bold"), bg="white").pack(anchor="e", padx=25)
        Entry(frame, textvariable=self.username_var, font=("Tahoma", 11), width=24, bd=2, relief="solid").pack(pady=5)

        Label(frame, text="كلمة المرور:", font=("Tahoma", 9, "bold"), bg="white").pack(anchor="e", padx=25)
        Entry(frame, textvariable=self.password_var, show="*", font=("Tahoma", 11), width=24, bd=2, relief="solid").pack(pady=5)

        Button(frame, text="دخول", font=("Tahoma", 10, "bold"), bg="#28a745", fg="white", width=20, bd=0, command=self.verify_login).pack(pady=15)

    def verify_login(self):
        uname = self.username_var.get().strip()
        upass = self.password_var.get().strip()

        if not uname or not upass:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم المستخدم وكلمة المرور.")
            return

        role = database.check_user_login(uname, upass)
        if role:
            messagebox.showinfo("نجاح", f"مرحباً بك ({uname})\nالصلاحية: {role}")
            self.root.destroy()
            open_main_app(role)
        else:
            messagebox.showerror("فشل الدخول", "اسم المستخدم أو كلمة المرور غير صحيحة!")


# --- التطبيق الرئيسي لنقطة البيع والإدارة ---
def open_main_app(user_role):
    app = Tk()
    app.title("منظومة إدارة المحلات ونقطة البيع الحديثة")
    app.geometry("1150x720")
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
            messagebox.showerror("خطأ", "الرجاء تعبئة جميع الحقول المطلوبة.")
            return

        try:
            price = float(p_price)
            qty = int(p_qty)
        except ValueError:
            messagebox.showerror("خطأ", "السعر يجب أن يكون رقماً والكمية عدداً صحيحاً.")
            return

        success = database.add_product(b_code, p_name, price, qty)
        if success:
            messagebox.showinfo("نجاح", "تم إضافة المنتج بنجاح.")
            clear_entries()
            load_data()
        else:
            messagebox.showerror("خطأ", "رقم الباركود هذا موجود مسبقاً!")

    def update_item():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("تنبيه", "الرجاء اختيار منتج لتعديله من الجدول.")
            return
        
        values = tree.item(selected_item, 'values')
        product_id = values[0]

        b_code = barcode_var.get().strip()
        p_name = name_var.get().strip()
        p_price = price_var.get().strip()
        p_qty = qty_var.get().strip()

        if not b_code or not p_name or not p_price or not p_qty:
            messagebox.showerror("خطأ", "الرجاء تعبئة جميع الحقول.")
            return

        try:
            price = float(p_price)
            qty = int(p_qty)
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيم صحيحة للسعر والكمية.")
            return

        database.update_product(product_id, b_code, p_name, price, qty)
        messagebox.showinfo("نجاح", "تم تحديث بيانات المنتج بنجاح.")
        clear_entries()
        load_data()

    def delete_item():
        if user_role != "مدير":
            messagebox.showerror("صلاحية مرفوضة", "عذراً، حذف المنتجات متاح فقط للمدير!")
            return

        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("تنبيه", "الرجاء اختيار منتج للحذف من الجدول.")
            return
        
        values = tree.item(selected_item, 'values')
        product_id = values[0]
        
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف المنتج المحدد؟"):
            database.delete_product(product_id)
            clear_entries()
            load_data()
            messagebox.showinfo("نجاح", "تم الحذف بنجاح.")

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
                messagebox.showinfo("بيع سريع", f"تم بيع: {p_name}\nالسعر: {p_price} د.ل\nرقم الفاتورة: {invoice_no}")
            else:
                messagebox.showwarning("تنبيه المخزون", f"عذراً، سلعة ({p_name}) نفدت من المخزون!")
        else:
            messagebox.showerror("خطأ", "رقم الباركود غير مسجل بالمنظومة!")
            pos_barcode_var.set("")

    def show_sales_report():
        report_win = Toplevel(app)
        report_win.title("تقارير المبيعات والفواتير المسجلة")
        report_win.geometry("800x450")
        report_win.config(bg="#f8f9fa")

        Label(report_win, text="📊 سجل مبيعات وفواتير المحل", font=("Tahoma", 13, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=10)

        rep_frame = Frame(report_win, bg="white")
        rep_frame.pack(fill="both", expand=True, padx=15, pady=10)

        scroll_r = Scrollbar(rep_frame, orient=VERTICAL)
        scroll_r.pack(side=RIGHT, fill=Y)

        rep_tree = ttk.Treeview(rep_frame, columns=("id", "inv", "name", "price", "qty", "total", "date"), show="headings", yscrollcommand=scroll_r.set)
        scroll_r.config(command=rep_tree.yview)

        rep_tree.heading("id", text="الرقم")
        rep_tree.heading("inv", text="رقم الفاتورة")
        rep_tree.heading("name", text="اسم السلعة")
        rep_tree.heading("price", text="السعر")
        rep_tree.heading("qty", text="الكمية")
        rep_tree.heading("total", text="الإجمالي")
        rep_tree.heading("date", text="الوقت والتاريخ")

        rep_tree.column("id", width=50, anchor=CENTER)
        rep_tree.column("inv", width=110, anchor=CENTER)
        rep_tree.column("name", width=180, anchor=CENTER)
        rep_tree.column("price", width=80, anchor=CENTER)
        rep_tree.column("qty", width=60, anchor=CENTER)
        rep_tree.column("total", width=90, anchor=CENTER)
        rep_tree.column("date", width=150, anchor=CENTER)

        rep_tree.pack(fill="both", expand=True)

        sales_data = database.get_all_sales()
        total_sales_revenue = 0
        for s in sales_data:
            total_sales_revenue += s[5]
            rep_tree.insert("", END, values=s)

        Label(report_win, text=f"Total Sales Revenue: {total_sales_revenue:.2f} LYD", font=("Tahoma", 11, "bold"), bg="#f8f9fa", fg="#27ae60").pack(pady=10)

    def show_item_card():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("تنبيه", "الرجاء اختيار منتج لعرض بطاقته.")
            return
        
        values = tree.item(selected_item, 'values')
        
        card_window = Toplevel(app)
        card_window.title("بطاقة الصنف والباركود")
        card_window.geometry("420x340")
        card_window.config(bg="white")
        
        Label(card_window, text="بطاقة تعريف السلعة", font=("Tahoma", 14, "bold"), bg="white", fg="#007bff").pack(pady=10)
        
        info_frame = Frame(card_window, bg="white")
        info_frame.pack(fill="x", padx=30, pady=8)
        
        Label(info_frame, text=f"اسم الصنف: {values[2]}", font=("Tahoma", 11, "bold"), bg="white", anchor="w").pack(fill="x", pady=3)
        Label(info_frame, text=f"السعر: {values[3]} د.ل", font=("Tahoma", 10), bg="white", fg="#27ae60", anchor="w").pack(fill="x", pady=3)
        Label(info_frame, text=f"الكمية المتاحة: {values[4]} قطعة", font=("Tahoma", 10), bg="white", fg="#e67e22", anchor="w").pack(fill="x", pady=3)
        Label(card_window, text=f"Barcode: *{values[1]}*", font=("Consolas", 14, "bold"), bg="white", fg="#333").pack(pady=15)
        
        Button(card_window, text="طباعة البطاقة", font=("Tahoma", 10, "bold"), bg="#007bff", fg="white", bd=0, padx=15, pady=5, command=lambda: messagebox.showinfo("طباعة", "تم إرسال بطاقة السلعة إلى طابعة الباركود بنجاح!")).pack(pady=10)

    header_frame = Frame(app, bg="#2c3e50", height=65)
    header_frame.pack(fill="x")
    Label(header_frame, text="🛒 منظومة إدارة المحلات ونقطة البيع الحديثة", font=("Tahoma", 15, "bold"), bg="#2c3e50", fg="white").pack(side=LEFT, padx=20)
    Label(header_frame, text=f"User: ({user_role}) | Dev: Alzool", font=("Tahoma", 10, "bold"), bg="#2c3e50", fg="#f39c12").pack(side=RIGHT, padx=20)

    main_container = Frame(app, bg="#f8f9fa")
    main_container.pack(fill="both", expand=True, padx=15, pady=15)

    lf_manage = LabelFrame(main_container, text=" بيانات المنتج والباركود ", font=("Tahoma", 11, "bold"), bg="#f8f9fa")
    lf_manage.pack(fill="x", pady=(0, 10))

    Label(lf_manage, text="اسم السلعة:", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=0, column=3, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=name_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=0, column=2, padx=5, pady=8)

    Label(lf_manage, text="رقم الباركود:", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=0, column=1, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=barcode_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=0, column=0, padx=5, pady=8)

    Label(lf_manage, text="السعر (د.ل):", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=1, column=3, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=price_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=1, column=2, padx=5, pady=8)

    Label(lf_manage, text="الكمية:", font=("Tahoma", 10, "bold"), bg="#f8f9fa").grid(row=1, column=1, sticky="e", padx=5, pady=8)
    Entry(lf_manage, textvariable=qty_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=1, column=0, padx=5, pady=8)

    control_frame = Frame(main_container, bg="#f8f9fa")
    control_frame.pack(fill="x", pady=5)

    lf_pos = LabelFrame(control_frame, text="⚡ نقطة البيع السريع", font=("Tahoma", 10, "bold"), bg="#e8f4f8")
    lf_pos.pack(side=LEFT, fill="x", expand=True, padx=(0, 5))
    Label(lf_pos, text="مرر الباركود:", font=("Tahoma", 9, "bold"), bg="#e8f4f8").pack(side=LEFT, padx=5)
    pos_entry = Entry(lf_pos, textvariable=pos_barcode_var, font=("Tahoma", 11), width=15, bd=2, relief="groove")
    pos_entry.pack(side=LEFT, padx=5)
    pos_entry.bind("<Return>", process_barcode_sale)
    Button(lf_pos, text="بيع سريع", font=("Tahoma", 9, "bold"), bg="#17a2b8", fg="white", bd=0, padx=10, command=process_barcode_sale).pack(side=LEFT, padx=5)

    lf_search = LabelFrame(control_frame, text="🔍 بحث عن منتج", font=("Tahoma", 10, "bold"), bg="#f8f9fa")
    lf_search.pack(side=RIGHT, fill="x", expand=True, padx=(5, 0))
    Label(lf_search, text="ابحث بالاسم/الباركود:", font=("Tahoma", 9), bg="#f8f9fa").pack(side=LEFT, padx=5)
    search_entry = Entry(lf_search, textvariable=search_var, font=("Tahoma", 11), width=15, bd=2, relief="groove")
    search_entry.pack(side=LEFT, padx=5)
    search_entry.bind("<KeyRelease>", search_item)

    btns_frame = Frame(main_container, bg="#f8f9fa", pady=10)
    btns_frame.pack(fill="x")

    Button(btns_frame, text="➕ إضافة منتج", font=("Tahoma", 9, "bold"), bg="#28a745", fg="white", bd=0, padx=8, pady=5, command=add_item).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="✏️ تعديل المنتج", font=("Tahoma", 9, "bold"), bg="#ffc107", fg="#333", bd=0, padx=8, pady=5, command=update_item).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="🗑️ حذف المحدد", font=("Tahoma", 9, "bold"), bg="#dc3545", fg="white", bd=0, padx=8, pady=5, command=delete_item).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="📊 تقارير المبيعات", font=("Tahoma", 9, "bold"), bg="#6f42c1", fg="white", bd=0, padx=8, pady=5, command=show_sales_report).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="🏷️ بطاقة السلعة", font=("Tahoma", 9, "bold"), bg="#007bff", fg="white", bd=0, padx=8, pady=5, command=show_item_card).pack(side=LEFT, expand=True, padx=2)
    Button(btns_frame, text="🧹 تفريغ الحقول", font=("Tahoma", 9, "bold"), bg="#6c757d", fg="white", bd=0, padx=8, pady=5, command=clear_entries).pack(side=LEFT, expand=True, padx=2)

    table_frame = Frame(main_container, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True, pady=5)

    scroll_y = Scrollbar(table_frame, orient=VERTICAL)
    scroll_y.pack(side=RIGHT, fill=Y)

    tree = ttk.Treeview(table_frame, columns=("id", "barcode", "name", "price", "qty"), show="headings", yscrollcommand=scroll_y.set)
    scroll_y.config(command=tree.yview)

    tree.heading("id", text="الرقم")
    tree.heading("barcode", text="رقم الباركود")
    tree.heading("name", text="اسم السلعة")
    tree.heading("price", text="السعر (د.ل)")
    tree.heading("qty", text="الكمية المتاحة")

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
