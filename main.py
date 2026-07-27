from tkinter import *
from tkinter import ttk, messagebox
import database
import sqlite3

root = Tk()
root.title("نظام إدارة المبيعات والمخزون الاحترافي - POS")
root.geometry("1050x720")
root.config(bg="#f8f9fa")

# تخصيص ثيم الأشكال والجدول (Styling)
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Tahoma", 11, "bold"), background="#343a40", foreground="white")
style.configure("Treeview", font=("Tahoma", 10), rowheight=25)
style.map("Treeview", background=[('selected', '#007bff')])

# المتغيرات
barcode_var = StringVar()
name_var = StringVar()
price_var = StringVar()
qty_var = StringVar()
search_var = StringVar()
pos_barcode_var = StringVar()

def clear_fields():
    barcode_var.set("")
    name_var.set("")
    price_var.set("")
    qty_var.set("")
    if 'selected_id' in globals():
        global selected_id
        selected_id = None

def load_data(data=None):
    for row in tree.get_children():
        tree.delete(row)
    
    records = data if data is not None else database.get_products()
    for row in records:
        tag = 'low_stock' if row[4] < 5 else 'normal'
        tree.insert("", END, values=row, tags=(tag,))
    
    total_val = database.get_total_inventory_value()
    lbl_total.config(text=f"إجمالي قيمة المخزون: {total_val:,.2f} د.ل")

def add_item():
    barcode = barcode_var.get().strip()
    name = name_var.get().strip()
    price = price_var.get().strip()
    qty = qty_var.get().strip()

    if barcode == "" or name == "" or price == "" or qty == "":
        messagebox.showerror("خطأ", "الرجاء تعبئة كافة الحقول المطلوبة!")
        return

    try:
        price = float(price)
        qty = int(qty)
        database.add_product(barcode, name, price, qty)
        messagebox.showinfo("نجاح", "تمت إضافة المنتج بنجاح.")
        clear_fields()
        load_data()
    except sqlite3.IntegrityError:
        messagebox.showerror("خطأ مكرر", "رقم الباركود هذا مسجل مسبقاً لمنتج آخر!")
    except ValueError:
        messagebox.showerror("خطأ", "تأكد أن السعر رقم والكمية عدد صحيح!")

def get_row_data(event):
    global selected_id
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item, 'values')
        selected_id = values[0]
        barcode_var.set(values[1])
        name_var.set(values[2])
        price_var.set(values[3])
        qty_var.set(values[4])

def update_item():
    if 'selected_id' not in globals() or not selected_id:
        messagebox.showwarning("تنبيه", "الرجاء تحديد منتج من الجدول لتعديله.")
        return
    
    barcode = barcode_var.get().strip()
    name = name_var.get().strip()
    price = price_var.get().strip()
    qty = qty_var.get().strip()

    if barcode == "" or name == "" or price == "" or qty == "":
        messagebox.showerror("خطأ", "الرجاء تعبئة كافة الحقول!")
        return

    try:
        price = float(price)
        qty = int(qty)
        database.update_product(selected_id, barcode, name, price, qty)
        messagebox.showinfo("نجاح", "تم تحديث المنتج بنجاح.")
        clear_fields()
        load_data()
    except ValueError:
        messagebox.showerror("خطأ", "البيانات المدخلة غير صالحة!")

def delete_item():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("تنبيه", "الرجاء تحديد منتج من الجدول للحذف.")
        return
    
    if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف المنتج المحدد؟"):
        for item in selected_item:
            values = tree.item(item, 'values')
            database.delete_product(values[0])
        clear_fields()
        load_data()
        messagebox.showinfo("نجاح", "تم الحذف بنجاح.")

def search_item(event):
    term = search_var.get()
    results = database.search_products(term)
    load_data(results)

def show_item_card():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("تنبيه", "الرجاء اختيار منتج لعرض بطاقته.")
        return
    
    values = tree.item(selected_item, 'values')
    
    card_window = Toplevel(root)
    card_window.title("بطاقة الصنف والباركود")
    card_window.geometry("420x340")
    card_window.config(bg="white")
    
    Label(card_window, text="بطاقة تعريف السلعة", font=("Tahoma", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=12)
    
    Frame(card_window, height=2, bg="#e0e0e0", width=360).pack(pady=2)
    
    info_frame = Frame(card_window, bg="white")
    info_frame.pack(fill="x", padx=30, pady=8)
    
    Label(info_frame, text=f"اسم الصنف: {values[2]}", font=("Tahoma", 11, "bold"), bg="white", anchor="w").pack(fill="x", pady=2)
    Label(info_frame, text=f"السعر: {values[3]} د.ل", font=("Tahoma", 10), bg="white", fg="#27ae60", anchor="w").pack(fill="x", pady=2)
    Label(info_frame, text=f"الكمية المتاحة: {values[4]} قطعة", font=("Tahoma", 10), bg="white", anchor="w").pack(fill="x", pady=2)
    
    Label(card_window, text=f"| |  |\n*{values[1]}*", font=("Consolas", 14, "bold"), bg="white", fg="#333").pack(pady=8)
    
    # توقيع العلامة في البطاقة
    Label(card_window, text="تطوير: الزول", font=("Tahoma", 8, "italic"), bg="white", fg="#888").pack(pady=2)
    
    Button(card_window, text="طباعة البطاقة", font=("Tahoma", 10, "bold"), bg="#007bff", fg="white", bd=0, padx=15, pady=5, command=lambda: messagebox.showinfo("طباعة", "تم إرسال بطاقة السلعة للطابعة بنجاح!")).pack(pady=5)

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
            load_data()
            pos_barcode_var.set("")
            messagebox.showinfo("عملية بيع سريعة", f"تم بيع: {p_name}\nالسعر: {p_price} د.ل\nالمتبقي بالمخزون: {new_qty}")
        else:
            messagebox.showwarning("نفاد المخزون", f"عذراً، سلعة ({p_name}) نفدت بالكامل من المخزون!")
    else:
        messagebox.showerror("خطأ", "رقم الباركود غير مسجل بالمنظومة!")
        pos_barcode_var.set("")


# --- بناء الواجهة بتصميم عصري وبصمة (الزول) ---

# الشريط العلوي الاحترافي مع توقيع العلامة
header_frame = Frame(root, bg="#2c3e50", height=65)
header_frame.pack(fill="x")

Label(header_frame, text="🛒 منظومة إدارة المحلات ونقطة البيع الحديثة", font=("Tahoma", 15, "bold"), bg="#2c3e50", fg="white").pack(side=RIGHT, padx=20, pady=15)
Label(header_frame, text="✨ [ تصميم : الزول ]", font=("Tahoma", 11, "bold"), bg="#2c3e50", fg="#f39c12").pack(side=LEFT, padx=20, pady=15)

# الحاويات الرئيسية
main_container = Frame(root, bg="#f8f9fa")
main_container.pack(fill="both", expand=True, padx=15, pady=15)

# 1. إطار البيانات والإدخال
lf_manage = LabelFrame(main_container, text=" بيانات المنتج والباركود ", font=("Tahoma", 11, "bold"), bg="#f8f9fa", fg="#2c3e50", padx=15, pady=15)
lf_manage.pack(fill="x", pady=(0, 10))

# صف الإدخال الأول
lbl_barcode = Label(lf_manage, text="رقم الباركود:", font=("Tahoma", 10, "bold"), bg="#f8f9fa")
lbl_barcode.grid(row=0, column=3, sticky="e", padx=5, pady=8)
Entry(lf_manage, textvariable=barcode_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=0, column=2, padx=10, pady=8)

lbl_name = Label(lf_manage, text="اسم السلعة:", font=("Tahoma", 10, "bold"), bg="#f8f9fa")
lbl_name.grid(row=0, column=1, sticky="e", padx=5, pady=8)
Entry(lf_manage, textvariable=name_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=0, column=0, padx=10, pady=8)

# صف الإدخال الثاني
lbl_price = Label(lf_manage, text="السعر (د.ل):", font=("Tahoma", 10, "bold"), bg="#f8f9fa")
lbl_price.grid(row=1, column=3, sticky="e", padx=5, pady=8)
Entry(lf_manage, textvariable=price_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=1, column=2, padx=10, pady=8)
lbl_qty = Label(lf_manage, text="الكمية:", font=("Tahoma", 10, "bold"), bg="#f8f9fa")
lbl_qty.grid(row=1, column=1, sticky="e", padx=5, pady=8)
Entry(lf_manage, textvariable=qty_var, font=("Tahoma", 11), width=22, bd=2, relief="groove").grid(row=1, column=0, padx=10, pady=8)


# 2. إطار نقطة البيع السريع (POS) والبحث
control_frame = Frame(main_container, bg="#f8f9fa")
control_frame.pack(fill="x", pady=5)

# نقطة البيع بالبار كود
lf_pos = LabelFrame(control_frame, text=" ⚡️ نقطة البيع السريع ", font=("Tahoma", 10, "bold"), bg="#e8f4f8", fg="#0275d8", padx=10, pady=10)
lf_pos.pack(side=LEFT, fill="x", expand=True, padx=(0, 5))

Label(lf_pos, text="مرر الباركود للبيع المباشر:", font=("Tahoma", 9, "bold"), bg="#e8f4f8").pack(side=LEFT, padx=5)
pos_entry = Entry(lf_pos, textvariable=pos_barcode_var, font=("Tahoma", 11), width=18, bd=2, relief="groove")
pos_entry.pack(side=LEFT, padx=5)
pos_entry.bind("<Return>", process_barcode_sale)
Button(lf_pos, text="بيع سريع ↵", font=("Tahoma", 9, "bold"), bg="#17a2b8", fg="white", bd=0, padx=10, pady=4, command=process_barcode_sale).pack(side=LEFT, padx=5)

# البحث الذكي
lf_search = LabelFrame(control_frame, text=" 🔍 بحث عن منتج ", font=("Tahoma", 10, "bold"), bg="#f8f9fa", fg="#2c3e50", padx=10, pady=10)
lf_search.pack(side=RIGHT, fill="x", expand=True, padx=(5, 0))

Label(lf_search, text="ابحث بالاسم أو الباركود:", font=("Tahoma", 9), bg="#f8f9fa").pack(side=LEFT, padx=5)
search_entry = Entry(lf_search, textvariable=search_var, font=("Tahoma", 11), width=18, bd=2, relief="groove")
search_entry.pack(side=LEFT, padx=5)
search_entry.bind("<KeyRelease>", search_item)


# 3. الأزرار الرئيسية بتصميم عصري وألوان متناسقة
btns_frame = Frame(main_container, bg="#f8f9fa", pady=10)
btns_frame.pack(fill="x")

Button(btns_frame, text="➕ إضافة منتج", font=("Tahoma", 10, "bold"), bg="#28a745", fg="white", bd=0, padx=12, pady=6, width=12, command=add_item).pack(side=LEFT, padx=4)
Button(btns_frame, text="✏️ تعديل المنتج", font=("Tahoma", 10, "bold"), bg="#ffc107", fg="#333", bd=0, padx=12, pady=6, width=12, command=update_item).pack(side=LEFT, padx=4)
Button(btns_frame, text="🗑️ حذف المحدد", font=("Tahoma", 10, "bold"), bg="#dc3545", fg="white", bd=0, padx=12, pady=6, width=12, command=delete_item).pack(side=LEFT, padx=4)
Button(btns_frame, text="🖨️ بطاقة السلعة", font=("Tahoma", 10, "bold"), bg="#007bff", fg="white", bd=0, padx=12, pady=6, width=14, command=show_item_card).pack(side=LEFT, padx=4)
Button(btns_frame, text="🧹 تفريغ الحقول", font=("Tahoma", 10), bg="#6c757d", fg="white", bd=0, padx=10, pady=6, width=11, command=clear_fields).pack(side=RIGHT, padx=4)


# 4. جدول عرض البيانات (Treeview)
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

# تنبيه بصري للمخزون المنخفض
tree.tag_configure('low_stock', background='#f8d7da')

# 5. الشريط السفلي لإجمالي المخزون والعلامة التجارية
footer_frame = Frame(root, bg="#343a40", height=45)
footer_frame.pack(fill="x", side=BOTTOM)

lbl_total = Label(footer_frame, text="إجمالي قيمة المخزون: 0.00 د.ل", font=("Tahoma", 11, "bold"), bg="#343a40", fg="white")
lbl_total.pack(side=RIGHT, padx=20, pady=10)
Label(footer_frame, text="© تم التطوير بواسطة: الزول", font=("Tahoma", 9, "bold"), bg="#343a40", fg="#f39c12").pack(side=LEFT, padx=20, pady=10)

load_data()
root.mainloop()