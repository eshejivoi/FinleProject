import sqlite3


def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Таблица users с UNIQUE constraint для telegram_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            username TEXT,
            email TEXT NOT NULL
        )
    ''')

    # Таблица requests
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


def migrate_add_unique():
    """Миграция для добавления UNIQUE constraint к telegram_id"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # Проверяем существование ограничения
        cursor.execute('''
            SELECT sql 
            FROM sqlite_master 
            WHERE type = 'table' 
            AND name = 'users'
        ''')
        table_info = cursor.fetchone()[0]

        if 'UNIQUE' not in table_info:
            # Создаем новую таблицу с UNIQUE
            cursor.execute('''
                CREATE TABLE new_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    username TEXT,
                    email TEXT NOT NULL
                )
            ''')

            # Копируем данные
            cursor.execute('''
                INSERT INTO new_users (id, telegram_id, username, email)
                SELECT id, telegram_id, username, email FROM users
            ''')

            # Заменяем таблицы
            cursor.execute('DROP TABLE users')
            cursor.execute('ALTER TABLE new_users RENAME TO users')

            conn.commit()
    except Exception as e:
        print(f"Ошибка миграции UNIQUE: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_user(telegram_id, username, email, request, status='ждет рассмотрения'):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        # Обновляем или добавляем пользователя
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
            VALUES (
                (SELECT id FROM users WHERE telegram_id = ?),
                ?, ?
            )
        ''', (telegram_id, request, status))

        conn.commit()
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")
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
        print(f"Ошибка обновления статуса: {e}")
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
    except Exception as e:
        print(f"Ошибка миграции статусов: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Последовательность выполнения миграций
    create_table()
    migrate_add_unique()  # Добавляем UNIQUE constraint
    migrate_old_statuses()  # Исправляем старые статусы
    print("Миграции успешно выполнены!")