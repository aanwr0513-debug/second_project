import sqlite3

def connect_db():
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            qty INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_product(barcode, name, price, qty):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (barcode, name, price, qty) VALUES (?, ?, ?, ?)", (barcode, name, price, qty))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, name, price, qty FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_products(search_term):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, name, price, qty FROM products WHERE name LIKE ? OR barcode LIKE ?", ('%' + search_term + '%', '%' + search_term + '%'))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_product_by_barcode(barcode):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, name, price, qty FROM products WHERE barcode = ?", (barcode,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_product(product_id, barcode, name, price, qty):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET barcode = ?, name = ?, price = ?, qty = ? WHERE id = ?", (barcode, name, price, qty, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def get_total_inventory_value():
    conn = sqlite3.connect("store_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(price * qty) FROM products")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0.0

connect_db()