import sqlite3

def get_connection():
    return sqlite3.connect("expanse.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS person (
        p_id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_name TEXT UNIQUE,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    );

    CREATE TABLE IF NOT EXISTS accounts (
        acc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        acc_no TEXT,
        acc_name TEXT,
        user_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS currency (
        cur_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cur_name TEXT,
        in_inr REAL,
        symbol TEXT
    );

    CREATE TABLE IF NOT EXISTS expanse (
        e_id INTEGER PRIMARY KEY AUTOINCREMENT,
        e_cat TEXT,
        e_date TEXT,
        e_amt REAL,
        e_curr_id INTEGER,
        e_acc_id INTEGER,
        user_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS credit (
        cred_id INTEGER PRIMARY KEY AUTOINCREMENT,
        acc_id INTEGER,
        c_amt REAL,
        c_curr_id INTEGER,
        c_date TEXT,
        user_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS borrow (
        b_id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_id INTEGER,
        b_amt REAL,
        b_curr_id INTEGER,
        borrow_date TEXT,
        repay_date TEXT,
        user_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS lending (
        l_id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_id INTEGER,
        l_amt REAL,
        l_curr_id INTEGER,
        acc_id INTEGER,
        user_id INTEGER
    );
    """)

    # Add default account "Cash" and default currencies
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE acc_name = 'Cash'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO accounts (acc_no, acc_name, user_id) VALUES (?, ?, ?)", ("CASH001", "Cash", 1))

    default_currencies = [
        ("INR", 1.0, "₹"),
        ("USD", 83.0, "$"),
        ("EUR", 91.0, "€"),
        ("GBP", 107.0, "£"),
        ("JPY", 0.57, "¥"),
        ("AUD", 55.0, "A$")
    ]
    for name, rate, sym in default_currencies:
        cursor.execute("SELECT COUNT(*) FROM currency WHERE cur_name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO currency (cur_name, in_inr, symbol) VALUES (?, ?, ?)", (name, rate, sym))

    conn.commit()
    conn.close()
