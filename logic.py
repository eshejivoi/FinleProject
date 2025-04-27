import sqlite3


def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            username TEXT,
            email TEXT NOT NULL
        )
    ''')

    # Создание таблицы requests с проверкой наличия колонки created_at
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

    # Проверяем наличие колонки created_at (для старых версий БД)
    cursor.execute('PRAGMA table_info(requests)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'created_at' not in columns:
        cursor.execute('ALTER TABLE requests ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

    conn.commit()
    conn.close()
# logic.py

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


# logic.py

# logic.py
def add_user(telegram_id, username, email, request, status='ждет рассмотрения'):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        # Обновляем или добавляем пользователя по telegram_id
        cursor.execute('''
            INSERT INTO users (telegram_id, username, email)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET 
                username=excluded.username,
                email=excluded.email
        ''', (telegram_id, username, email))

        # Добавляем запрос
        cursor.execute('''
            INSERT INTO requests (user_id, request, status)
            VALUES ((SELECT id FROM users WHERE telegram_id = ?), ?, ?)
        ''', (telegram_id, request, status))

        conn.commit()
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_user_requests(telegram_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.created_at, r.status, r.request
        FROM requests r
        JOIN users u ON r.user_id = u.id
        WHERE u.telegram_id = ?
        ORDER BY r.created_at DESC
    ''', (telegram_id,))
    requests = []
    for row in cursor.fetchall():
        requests.append({
            'created_at': row[0],
            'status': row[1],
            'request_text': row[2]
        })
    conn.close()
    return requests

def update_request_status(request_id, new_status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE requests 
            SET status = ?
            WHERE id = ?
        ''', (new_status, request_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_old_statuses():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE requests 
            SET status = 'ждет рассмотрения' 
            WHERE status LIKE 'Отправлено%'
        ''')
        conn.commit()
        print(f"Обновлено записей: {cursor.rowcount}")
    except Exception as e:
        print(f"Ошибка миграции: {e}")
    finally:
        conn.close()
# logic.py (дополнение к migrate_old_statuses)
def migrate_user_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        # Добавляем колонку telegram_id если она отсутствует
        cursor.execute('PRAGMA table_info(users)')
        columns = [column[1] for column in cursor.fetchall()]
        if 'telegram_id' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN telegram_id INTEGER')
            conn.commit()
    except Exception as e:
        print(f"Ошибка миграции: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_table()
    migrate_user_data()  # Новая миграция
    migrate_old_statuses()
