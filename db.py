import sqlite3

DB_NAME = "planner.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Exams table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            course TEXT,
            exam_date DATETIME,
            start_date DATETIME,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')


    # Tasks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_name TEXT,
            hours INTEGER,
            due_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Friends table
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

#username and login management functions
def check_username_exists(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return True  # Username exists
    else:
        return False  # Username does not exist

def create_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True # Return True if user created successfully, else False

def validate_user(username, entered_password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, entered_password))
    user = c.fetchone()
    conn.close()
    return True if user else False

#task management functions
def add_exam_to_db(username, course, exam_date, start_date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO exams (username, course, exam_date, start_date) VALUES (?, ?, ?, ?)",
              (username, course, exam_date, start_date))
    conn.commit()
    conn.close()

def get_exams(username):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # makes rows behave like dictionaries
    c = conn.cursor()
    c.execute("SELECT * FROM exams WHERE username=?", (username,))
    exams = c.fetchall()
    conn.close()
    return exams

def delete_exam(exam_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM exams WHERE id=?", (exam_id,))
    conn.commit()
    conn.close()

def troubleshoot():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM exams")
    tables = c.fetchall()
    conn.close()
    return tables