import hashlib
from db import get_connection
import sqlite3

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO person (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT p_id, password FROM person WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and result[1] == hash_password(password):
        return result[0]
    return None
