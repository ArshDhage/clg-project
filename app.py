from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__, template_folder=".")


def get_db():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():

    conn = get_db()

    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY id DESC"
    ).fetchall()

    income = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE type='income'"
    ).fetchone()[0] or 0

    expense = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE type='expense'"
    ).fetchone()[0] or 0

    balance = income - expense

    category_data = conn.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE type = 'expense'
        GROUP BY category
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expense=expense,
        balance=balance,
        category_data=category_data
    )


@app.route("/add", methods=["POST"])
def add_transaction():

    transaction_type = request.form["type"]
    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form["description"]
    date = request.form["date"]

    conn = get_db()

    conn.execute("""
        INSERT INTO transactions
        (type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_type,
        amount,
        category,
        description,
        date
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete_transaction(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":

    create_database()

    app.run(debug=True)
    
