from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import datetime
import csv
import os

app = Flask(__name__)

DB_NAME = 'expense_tracker.db'

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        trans_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)",
                  (trans_type, category, amount, date))
        conn.commit()
        return redirect('/')

    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = c.fetchall()

    income = sum(row[3] for row in transactions if row[1] == 'income')
    expense = sum(row[3] for row in transactions if row[1] == 'expense')
    balance = income - expense

    categories = list(set(row[2] for row in transactions))
    category_data = {cat: 0 for cat in categories}
    for row in transactions:
        if row[1] == 'expense':
            category_data[row[2]] += row[3]

    # Data for line chart (expenses over time)
    line_labels = [row[4] for row in transactions if row[1] == 'expense']
    line_values = [row[3] for row in transactions if row[1] == 'expense']

    conn.close()
    return render_template('index.html', transactions=transactions, income=income, expense=expense,
                           balance=balance, category_data=category_data,
                           line_labels=line_labels[::-1], line_values=line_values[::-1])

@app.route('/delete/<int:id>')
def delete_transaction(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/export_csv')
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    transactions = c.fetchall()
    conn.close()

    filename = 'transactions.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Type', 'Category', 'Amount', 'Date'])
        writer.writerows(transactions)

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
