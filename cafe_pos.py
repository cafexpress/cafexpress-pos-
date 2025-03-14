from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('cafe_pos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                item TEXT,
                price REAL,
                quantity INTEGER,
                total REAL,
                payment_method TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                stock INTEGER,
                price REAL
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'POST':
        item = request.form['item']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        total = price * quantity
        payment_method = request.form['payment_method']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect('cafe_pos.db')
        c = conn.cursor()
        c.execute("INSERT INTO sales (date, item, price, quantity, total, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
                  (date, item, price, quantity, total, payment_method))
        conn.commit()
        conn.close()
        return redirect(url_for('sales'))
    
    conn = sqlite3.connect('cafe_pos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sales")
    sales_data = c.fetchall()
    conn.close()
    return render_template('sales.html', sales=sales_data)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        item = request.form['item']
        stock = int(request.form['stock'])
        price = float(request.form['price'])
        
        conn = sqlite3.connect('cafe_pos.db')
        c = conn.cursor()
        c.execute("INSERT INTO inventory (item, stock, price) VALUES (?, ?, ?)",
                  (item, stock, price))
        conn.commit()
        conn.close()
        return redirect(url_for('inventory'))
    
    conn = sqlite3.connect('cafe_pos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    inventory_data = c.fetchall()
    conn.close()
    return render_template('inventory.html', inventory=inventory_data)

@app.route('/api/orders', methods=['POST'])
def api_orders():
    data = request.get_json()
    item = data['item']
    quantity = int(data['quantity'])
    payment_method = data['payment_method']
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect('cafe_pos.db')
    c = conn.cursor()
    c.execute("SELECT price FROM inventory WHERE item = ?", (item,))
    price_data = c.fetchone()
    if not price_data:
        return jsonify({"error": "Item not found"}), 400
    price = price_data[0]
    total = price * quantity
    
    c.execute("INSERT INTO sales (date, item, price, quantity, total, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
              (date, item, price, quantity, total, payment_method))
    c.execute("UPDATE inventory SET stock = stock - ? WHERE item = ?", (quantity, item))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Order processed successfully", "total": total})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
