import sqlite3

def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email) VALUES (?, ?)
        ''', (username, email))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Error: Username or email already exists.")
    finally:
        conn.close()
if __name__ == "__main__":
    create_table()