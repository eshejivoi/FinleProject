import sqlite3

from config import bot


@bot.callback_query_handler(func=lambda call: True)
def handle_questions(call):
    bot.answer_callback_query(callback_query_id=call.id)

    # Создаем пары вопрос-ответ
    qa = {
        "question_order": {
            "question": "Как оформить заказ?",
            "answer": """Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку "Добавить в корзину", затем перейдите в корзину и следуйте инструкциям для завершения покупки."""
        },
        "question_status": {
            "question": "Как узнать статус заказа?",
            "answer": """Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел "Мои заказы". Там будет указан текущий статус вашего заказа."""
        },
        "question_cancel": {
            "question": "Как отменить заказ?",
            "answer": "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки."
        },
        "question_broke": {
            "question": "Что делать, если товар пришел поврежденным?",
            "answer": "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара."
        },
        "question_support": {
            "question": "Как связаться с вашей технической поддержкой?",
            "answer": "Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота."
        },
        "question_delivery": {
            "question": "Как узнать информацию о доставке?",
            "answer": "Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки."
        }
    }

    data = qa.get(call.data)
    if data:
        # Редактируем оригинальное сообщение
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"❓ Вопрос: {data['question']}\n\n✅ Ответ: {data['answer']}",
            reply_markup=None
        )



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