from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

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

    conn.close()
    return render_template('index.html', transactions=transactions, income=income, expense=expense,
                           balance=balance, category_data=category_data)

if __name__ == '__main__':
    app.run(debug=True)
