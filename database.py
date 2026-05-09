import sqlite3
import hashlib
import os

DB_PATH = "school.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_number TEXT UNIQUE NOT NULL,
        enrolment_number TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        date_of_birth TEXT NOT NULL,
        gender TEXT NOT NULL,
        father_name TEXT NOT NULL,
        mother_name TEXT,
        guardian_name TEXT,
        guardian_phone TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        class_name TEXT NOT NULL,
        section TEXT,
        roll_number TEXT NOT NULL,
        blood_group TEXT,
        health_issues TEXT
    )''')

    # Teachers table
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        gender TEXT NOT NULL,
        qualification TEXT NOT NULL,
        joining_date TEXT NOT NULL,
        salary_amount REAL NOT NULL,
        salary_frequency TEXT NOT NULL,
        bank_account TEXT NOT NULL,
        ifsc_code TEXT NOT NULL,
        class_assigned TEXT,
        status TEXT NOT NULL
    )''')

    # Fee structure table
    c.execute('''CREATE TABLE IF NOT EXISTS fee_structure (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT UNIQUE NOT NULL,
        monthly_fee REAL NOT NULL
    )''')

    # Fee payments table
    c.execute('''CREATE TABLE IF NOT EXISTS fee_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_number TEXT NOT NULL,
        payment_date TEXT NOT NULL,
        amount_paid REAL NOT NULL,
        month_year TEXT NOT NULL,
        remarks TEXT
    )''')

    # Salary payments table
    c.execute('''CREATE TABLE IF NOT EXISTS salary_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        payment_date TEXT NOT NULL,
        amount_paid REAL NOT NULL,
        month_year TEXT NOT NULL,
        remarks TEXT
    )''')

    # Insert default admin
    c.execute("SELECT * FROM users WHERE login_id = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (login_id, password, name, role) VALUES (?, ?, ?, ?)",
                  ('admin', hash_password('password'), 'Administrator', 'Admin'))

    # Insert default fee structure for classes
    classes = get_list_of_classes()
    for i, cls in enumerate(classes):
        c.execute("SELECT * FROM fee_structure WHERE class_name = ?", (cls,))
        if not c.fetchone():
            base_fee = 500 + (i * 50)
            c.execute("INSERT INTO fee_structure (class_name, monthly_fee) VALUES (?, ?)", (cls, base_fee))

    conn.commit()
    conn.close()

def get_list_of_classes():
    return ["Nursery", "LKG", "UKG",
            "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
            "Class 6", "Class 7", "Class 8", "Class 9", "Class 10",
            "Class 11 (Science)", "Class 11 (Commerce)", "Class 11 (Arts)",
            "Class 12 (Science)", "Class 12 (Commerce)", "Class 12 (Arts)"]

# ─── USER FUNCTIONS ──────────────────────────────────────────────────────────

def authenticate_user(login_id, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE login_id = ? AND password = ?",
              (login_id, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, login_id, name, role FROM users WHERE login_id != 'admin'")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return users

def create_user(login_id, password, name, role):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (login_id, password, name, role) VALUES (?, ?, ?, ?)",
                  (login_id, hash_password(password), name, role))
        conn.commit()
        return True, "User created successfully."
    except sqlite3.IntegrityError:
        return False, "Login ID already exists."
    finally:
        conn.close()

def delete_user(login_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE login_id = ?", (login_id,))
    conn.commit()
    conn.close()

# ─── STUDENT FUNCTIONS ────────────────────────────────────────────────────────

def add_student(data):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO students VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (data['admission_number'], data['enrolment_number'], data['first_name'],
             data['last_name'], data['email'], data['date_of_birth'], data['gender'],
             data['father_name'], data['mother_name'], data['guardian_name'],
             data['guardian_phone'], data['address'], data['phone'], data['class_name'],
             data['section'], data['roll_number'], data['blood_group'], data['health_issues']))
        conn.commit()
        return True, "Student added successfully."
    except sqlite3.IntegrityError as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_student_by_admission(admission_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE admission_number = ?", (admission_number,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_student(admission_number, data):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''UPDATE students SET enrolment_number=?, first_name=?, last_name=?, email=?,
            date_of_birth=?, gender=?, father_name=?, mother_name=?, guardian_name=?,
            guardian_phone=?, address=?, phone=?, class_name=?, section=?, roll_number=?,
            blood_group=?, health_issues=? WHERE admission_number=?''',
            (data['enrolment_number'], data['first_name'], data['last_name'], data['email'],
             data['date_of_birth'], data['gender'], data['father_name'], data['mother_name'],
             data['guardian_name'], data['guardian_phone'], data['address'], data['phone'],
             data['class_name'], data['section'], data['roll_number'], data['blood_group'],
             data['health_issues'], admission_number))
        conn.commit()
        return True, "Student updated successfully."
    except sqlite3.IntegrityError as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

# ─── TEACHER FUNCTIONS ────────────────────────────────────────────────────────

def add_teacher(data):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO teachers VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (data['employee_id'], data['first_name'], data['last_name'], data['email'],
             data['phone'], data['date_of_birth'], data['gender'], data['qualification'],
             data['joining_date'], data['salary_amount'], data['salary_frequency'],
             data['bank_account'], data['ifsc_code'], data['class_assigned'], data['status']))
        conn.commit()
        return True, "Teacher added successfully."
    except sqlite3.IntegrityError as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_teacher_by_id(employee_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM teachers WHERE employee_id = ?", (employee_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_teacher(employee_id, data):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''UPDATE teachers SET first_name=?, last_name=?, email=?, phone=?,
            date_of_birth=?, gender=?, qualification=?, joining_date=?, salary_amount=?,
            salary_frequency=?, bank_account=?, ifsc_code=?, class_assigned=?, status=?
            WHERE employee_id=?''',
            (data['first_name'], data['last_name'], data['email'], data['phone'],
             data['date_of_birth'], data['gender'], data['qualification'], data['joining_date'],
             data['salary_amount'], data['salary_frequency'], data['bank_account'],
             data['ifsc_code'], data['class_assigned'], data['status'], employee_id))
        conn.commit()
        return True, "Teacher updated successfully."
    except sqlite3.IntegrityError as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

# ─── FEE FUNCTIONS ────────────────────────────────────────────────────────────

def get_fee_structure():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM fee_structure ORDER BY id")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_fee_for_class(class_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT monthly_fee FROM fee_structure WHERE class_name = ?", (class_name,))
    row = c.fetchone()
    conn.close()
    return row['monthly_fee'] if row else 0

def update_fee_structure(class_name, monthly_fee):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE fee_structure SET monthly_fee = ? WHERE class_name = ?", (monthly_fee, class_name))
    conn.commit()
    conn.close()

def get_fee_payments(admission_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM fee_payments WHERE admission_number = ? ORDER BY payment_date DESC",
              (admission_number,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_fee_payment(admission_number, payment_date, amount, month_year, remarks=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO fee_payments (admission_number, payment_date, amount_paid, month_year, remarks) VALUES (?,?,?,?,?)",
              (admission_number, payment_date, amount, month_year, remarks))
    conn.commit()
    conn.close()

# ─── SALARY FUNCTIONS ─────────────────────────────────────────────────────────

def get_salary_payments(employee_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM salary_payments WHERE employee_id = ? ORDER BY payment_date DESC",
              (employee_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_salary_payment(employee_id, payment_date, amount, month_year, remarks=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO salary_payments (employee_id, payment_date, amount_paid, month_year, remarks) VALUES (?,?,?,?,?)",
              (employee_id, payment_date, amount, month_year, remarks))
    conn.commit()
    conn.close()
