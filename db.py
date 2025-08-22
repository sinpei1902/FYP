import psycopg2
import psycopg2.extras
import streamlit as st

# Get DB connection string from Streamlit secrets
DB_URL = st.secrets["postgres"]["url"]

def get_conn():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Exams table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id SERIAL PRIMARY KEY,
            username TEXT,
            course TEXT,
            exam_date TIMESTAMP,
            start_date TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')

    # Tasks table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            task_name TEXT,
            hours INTEGER,
            due_date DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Friends table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()


# --- User management ---
def check_username_exists(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return bool(result)


def create_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cur.close()
    conn.close()
    return True


def validate_user(username, entered_password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, entered_password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return True if user else False


# --- Exam management ---
def add_exam_to_db(username, course, exam_date, start_date):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO exams (username, course, exam_date, start_date) VALUES (%s, %s, %s, %s)",
                (username, course, exam_date, start_date))
    conn.commit()
    cur.close()
    conn.close()


def get_exams(username):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # like sqlite3.Row
    cur.execute("SELECT * FROM exams WHERE username=%s", (username,))
    exams = cur.fetchall()
    cur.close()
    conn.close()
    return exams
