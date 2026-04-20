from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

db_file = 'gym.db'

# Package durations in months
PACKAGE_DURATIONS = {
    "Silver": 6,
    "Gold": 12,
    "Diamond": 24
}

def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Trainers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS trainers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        specialization TEXT NOT NULL,
                        phone TEXT NOT NULL
                    )''')

    # Members table
    cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT NOT NULL,
                        package TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        trainer_id INTEGER,
                        FOREIGN KEY(trainer_id) REFERENCES trainers(id)
                    )''')

    # Payments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        member_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        date TEXT NOT NULL,
                        method TEXT NOT NULL,
                        FOREIGN KEY(member_id) REFERENCES members(id)
                    )''')

    # Deleted members log table
    cursor.execute('''CREATE TABLE IF NOT EXISTS deleted_members (
                        id INTEGER,
                        name TEXT,
                        email TEXT,
                        phone TEXT,
                        package TEXT,
                        start_date TEXT,
                        end_date TEXT,
                        trainer_id INTEGER,
                        deleted_at TEXT
                    )''')

    # Trigger to log deleted members
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS log_deleted_member
        AFTER DELETE ON members
        BEGIN
            INSERT INTO deleted_members (
                id, name, email, phone, package, start_date, end_date, trainer_id, deleted_at
            )
            VALUES (
                OLD.id, OLD.name, OLD.email, OLD.phone, OLD.package,
                OLD.start_date, OLD.end_date, OLD.trainer_id, datetime('now')
            );
        END;
    ''')

    conn.commit()
    conn.close()


# Main landing page
@app.route('/')
def main():
    return render_template('main.html')

# ---------------- Member Routes ----------------
@app.route('/members')
def member_page():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    cursor.execute("SELECT id, name FROM trainers")
    trainers = cursor.fetchall()

    cursor.execute('''SELECT payments.*, members.name 
                      FROM payments JOIN members ON payments.member_id = members.id''')
    payments = cursor.fetchall()

    conn.close()
    return render_template('member.html', members=members, trainers=trainers, payments=payments)

@app.route('/add', methods=['POST'])
def add_member():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    package = request.form['package']
    trainer_id = request.form.get('trainer_id')

    start_date = datetime.today().strftime('%Y-%m-%d')
    end_date = (datetime.today() + timedelta(days=PACKAGE_DURATIONS[package] * 30)).strftime('%Y-%m-%d')

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO members (name, email, phone, package, start_date, end_date, trainer_id)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (name, email, phone, package, start_date, end_date, trainer_id))
    conn.commit()
    conn.close()
    return redirect(url_for('member_page'))

@app.route('/update/<int:id>', methods=['POST'])
def update_member(id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    package = request.form['package']
    trainer_id = request.form.get('trainer_id')

    start_date = datetime.today().strftime('%Y-%m-%d')
    end_date = (datetime.today() + timedelta(days=PACKAGE_DURATIONS[package] * 30)).strftime('%Y-%m-%d')

    with sqlite3.connect(db_file, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE members 
                          SET name=?, email=?, phone=?, package=?, start_date=?, end_date=?, trainer_id=?
                          WHERE id=?''',
                       (name, email, phone, package, start_date, end_date, trainer_id, id))
        conn.commit()

    return redirect(url_for('member_page'))

@app.route('/delete/<int:id>')
def delete_member(id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('member_page'))

# ---------------- Trainer Routes ----------------

@app.route('/trainers')
def trainer_page():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trainers")
    trainers = cursor.fetchall()
    conn.close()
    return render_template('trainer.html', trainers=trainers)

@app.route('/trainer/add', methods=['POST'])
def add_trainer():
    name = request.form['name']
    specialization = request.form['specialization']
    phone = request.form['phone']

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trainers (name, specialization, phone) VALUES (?, ?, ?)",
                   (name, specialization, phone))
    conn.commit()
    conn.close()
    return redirect(url_for('trainer_page'))

@app.route('/trainer_update/<int:id>', methods=['POST'])
def update_trainer(id):
    name = request.form['name']
    specialization = request.form['specialization']
    phone = request.form['phone']

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE trainers SET name=?, specialization=?, phone=? WHERE id=?",
                   (name, specialization, phone, id))
    conn.commit()
    conn.close()
    return redirect(url_for('trainer_page'))

@app.route('/trainer/delete/<int:id>')
def delete_trainer(id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trainers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('trainer_page'))

# ---------------- Payment Page ----------------
@app.route('/payment')
def payment_page():
    with sqlite3.connect(db_file, check_same_thread=False) as conn:
        cursor = conn.cursor()

        # Fetch members for dropdown
        cursor.execute("SELECT id, name FROM members")
        members = cursor.fetchall()
        print("Fetched Members:", members)  # ✅ Check this in terminal

        # Fetch existing payments (if needed)
        cursor.execute("""
            SELECT payments.id, members.name, payments.amount, payments.date, payments.method
            FROM payments
            JOIN members ON payments.member_id = members.id
        """)
        payments = cursor.fetchall()

    return render_template("payment.html", members=members, payments=payments)
@app.route('/payment/add', methods=['POST'])
def add_payment():
    member_id = request.form['member_id']
    amount = request.form['amount']
    method = request.form['method']
    date = datetime.today().strftime('%Y-%m-%d')

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (member_id, amount, date, method) VALUES (?, ?, ?, ?)",
                   (member_id, amount, date, method))
    conn.commit()
    conn.close()
    return redirect(url_for('payment_page'))


@app.route('/payment/delete/<int:id>')
def delete_payment(id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('payment_page'))
@app.route('/deleted_members')
def deleted_members_page():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deleted_members")
    deleted_members = cursor.fetchall()
    conn.close()
    return render_template('deleted_members.html', deleted_members=deleted_members)


# ---------------- Run App ----------------

if __name__ == '__main__':
    init_db() 
    app.run(debug=True)


