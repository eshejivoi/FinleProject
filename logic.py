import sqlite3


def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Создание таблицы users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
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

def add_user(username, email, request, status='Отправлено'):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        # Обновляем или добавляем пользователя
        cursor.execute('''
            INSERT INTO users (username, email)
            VALUES (?, ?)
            ON CONFLICT(username) DO UPDATE SET email=excluded.email
        ''', (username, email))

        # Получаем user_id
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]

        # Добавляем запрос
        cursor.execute('''
            INSERT INTO requests (user_id, request, status)
            VALUES (?, ?, ?)
        ''', (user_id, request, status))

        conn.commit()
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()

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

if __name__ == "__main__":
    create_table()
    migrate_old_statuses()  # Вызов миграции
