import sqlite3
from datetime import datetime

def connect_db():
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    
    # جدول المنتجات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT,
            price REAL,
            qty INTEGER
        )
    """)
    
    # جدول المبيعات والفواتير
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT,
            product_name TEXT,
            price REAL,
            qty INTEGER,
            total REAL,
            date_time TEXT
        )
    """)
    
    # جدول المستخدمين والصلاحيات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    
    # إضافة حساب مدير افتراضي (Admin) إذا لم يكن موجوداً
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ('admin', '1234', 'مدير'))
        
    conn.commit()
    conn.close()

def add_product(barcode, name, price, qty):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (barcode, name, price, qty) VALUES (?, ?, ?, ?)",
            (barcode, name, price, qty)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_products():
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_product(product_id, barcode, name, price, qty):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET barcode = ?, name = ?, price = ?, qty = ? WHERE id = ?",
        (barcode, name, price, qty, product_id)
    )
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def search_products(term):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE barcode LIKE ? OR name LIKE ?"
    cursor.execute(query, ('%' + term + '%', '%' + term + '%'))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_product_by_barcode(barcode):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()
    conn.close()
    return product

# --- دوال المبيعات والفواتير ---
def record_sale(invoice_no, product_name, price, qty):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    total = price * qty
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO sales (invoice_no, product_name, price, qty, total, date_time) VALUES (?, ?, ?, ?, ?, ?)",
        (invoice_no, product_name, price, qty, total, date_time)
    )
    conn.commit()
    conn.close()

def get_all_sales():
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- دوال التحقق من المستخدمين ---
def check_user_login(username, password):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# تهيئة قاعدة البيانات والجداول تلقائياً
connect_db()
