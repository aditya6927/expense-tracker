import sqlite3 as sql;
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)

app.secret_key = "supersecretkey123"
# helper function to connect to database
def get_db_connection():
    conn = sql.connect('users.db')
    conn.row_factory = sql.Row
    return conn

# create user table if it does not exists
def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
        )
        ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category REXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
    conn.commit()
    conn.close()
#running database initialization when the app starts
init_db()

# Home page
@app.route('/') 
def home():
    if "username" not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()

    if user:
        total = conn.execute("""
            SELECT COUNT(*) FROM expenses 
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (user['id'], str(current_year), f"{current_month:02}")).fetchone()[0]

        expenses = conn.execute("""
            SELECT * FROM expenses 
            WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC
            LIMIT ? OFFSET ?
        """, (user['id'], str(current_year), f"{current_month:02}", per_page, offset)).fetchall()
        
        conn.close()

        total_pages = (total + per_page - 1) // per_page

        return render_template('home.html', expenses=expenses, page=page, total_pages=total_pages)

    return redirect(url_for('login'))

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # You will handle form data here
        username = request.form['username']
        password = request.form['password'] # sores hashed version in the db
        hashed_password = generate_password_hash(password)
        # connect to database and insert user
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            session['username'] = username # auto login
            print(f"registered and logged in: {username}")
            return redirect(url_for('home'))
        except sql.IntegrityError:
            flash("Username already exists")
        finally:
            conn.close()
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Handle login here
        username = request.form['username']
        password = request.form['password']

        # check if user exists
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['username'] = username # store in session
            flash("Logged in successfully")
            print(f"logged in: {username}")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/add', methods = ['GET', 'POST'])
def add_expense():
    if "username" not in session :
        return redirect(url_for('login'))

    if(request.method == 'POST'):
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        description = request.form["description"]

        # get user id
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
        if user:
            user_id = user['id']
            conn.execute("""
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)""", (user_id, amount, category, date, description)
                )
            conn.commit()
            flash("Expense added successfully")
        else :
            print("User not found")
        conn.close()
        return redirect(url_for('home'))
    return render_template("add_expense.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("logged out")
    return redirect(url_for('login'))

@app.route('/delete/<int:expense_id>', methods = ["POST"])
def delete_expense(expense_id):
    if("username" not in session):
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
    if user:
        conn.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user['id']))
        conn.commit()
        flash("Expense deleted")
    conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:expense_id>', methods = ['GET', 'POST'])
def edit_expense(expense_id):
    if("username" not in session):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
    if user :
        expense = conn.execute("SELECT * FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user['id'])).fetchone()

        if(request.method == "POST"):
            #get updated data from form
            category = request.form['category']
            amount = request.form['amount']
            description = request.form['description']

            if not category or not amount or not description:
                error_message = "All fields are required"
                return render_template('edit_expense.html', expense = expense, error_message = error_message)

            #update expense in db
            conn.execute("UPDATE expenses SET category = ?, amount = ?, description = ? WHERE id = ? AND user_id = ?",
                         (category, amount, description, expense_id, user['id']))
            conn.commit()
            flash("Expense added successfully.")
            return redirect(url_for('home'))
        return render_template("edit_expense.html", expense = expense)
    conn.close()
    return redirect(url_for('login'))

@app.route('/summary')
def summary():
    if "username" not in session :
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
    if user:
        expenses = conn.execute('SELECT * FROM expenses WHERE user_id = ?', (user['id'],)).fetchall()

        total_expenses = sum(expense['amount'] for expense in expenses)

        #filter by category or date
        category_filter = request.args.get('category')
        date_filter = request.args.get('date')
        if(category_filter):
            expenses = [expense for expense in expenses if(expense['category'] == category_filter)]
        if(date_filter):
            expenses = [expense for expense in expenses if(expense['date'] == date_filter)]
        return render_template("summary.html", expenses = expenses, total_expenses = total_expenses)
    conn.close()
    return redirect(url_for('login'))

# to delete users.db and expenses.db
# @app.route('/clear-data')
# def clear_data():
#     conn = get_db_connection()
#     conn.execute("DELETE FROM expenses")
#     conn.execute("DELETE FROM users")
#     conn.commit()
#     conn.close()
#     return "All data deleted. You can now remove this route."

if __name__ == '__main__':
    app.run(debug=True)
