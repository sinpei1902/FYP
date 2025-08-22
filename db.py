import psycopg2
import streamlit as st

# Get the DB URL from Streamlit secrets
DB_URL = st.secrets["postgres"]["url"]

# Utility function to get connection
def get_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

# Initialize database tables
def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Exams table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id SERIAL PRIMARY KEY,
            username TEXT REFERENCES users(username),
            course TEXT,
            exam_date TIMESTAMP,
            start_date TIMESTAMP
        )
    ''')

    # Tasks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            task_name TEXT,
            hours INTEGER,
            due_date TIMESTAMP
        )
    ''')

    # Friends table
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            friend_id INTEGER REFERENCES users(id)
        )
    ''')

    conn.commit()
    c.close()
    conn.close()

# ---------------------------
# User management functions
# ---------------------------
def check_username_exists(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    result = c.fetchone()
    c.close()
    conn.close()
    return True if result else False

def create_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    c.close()
    conn.close()
    return True

def validate_user(username, entered_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, entered_password))
    user = c.fetchone()
    c.close()
    conn.close()
    return True if user else False

# ---------------------------
# Exam management functions
# ---------------------------
def add_exam_to_db(username, course, exam_date, start_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO exams (username, course, exam_date, start_date) VALUES (%s, %s, %s, %s)",
        (username, course, exam_date, start_date)
    )
    conn.commit()
    c.close()
    conn.close()

def get_exams(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exams WHERE username=%s", (username,))
    exams = c.fetchall()
    c.close()
    conn.close()
    return exams

def delete_exam(exam_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM exams WHERE id=%s", (exam_id,))
    conn.commit()
    c.close()
    conn.close()

def troubleshoot():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exams")
    tables = c.fetchall()
    c.close()
    conn.close()
    return tables
