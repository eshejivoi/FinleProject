import sqlite3

def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            request TEXT NOT NULL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, email, request, status='Отправлено'):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email)
            VALUES (?, ?)
            ON CONFLICT(username) DO UPDATE SET email=excluded.email
        ''', (username, email))
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]
        cursor.execute('''
            INSERT INTO requests (user_id, request, status)
            VALUES (?, ?, ?)
        ''', (user_id, request, status))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_user_requests(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.created_at, r.status, r.request
        FROM requests r
        JOIN users u ON r.user_id = u.id
        WHERE u.id = ?
        ORDER BY r.created_at DESC
    ''', (user_id,))
    requests = []
    for row in cursor.fetchall():
        requests.append({
            'created_at': row[0],
            'status': row[1],
            'request_text': row[2]
        })
    conn.close()
    return requests

if __name__ == "__main__":
    create_table()