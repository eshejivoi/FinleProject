from config import bot, ADMINS
from telebot import types
import logic

hideBoard = types.ReplyKeyboardRemove()
user_data = {}

# Добавляем в начало main.py словарь с вопросами и ответами
QA = {
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


# Добавляем обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data in QA)
def handle_qa_callback(call):
    """Обработчик нажатий на кнопки с вопросами"""
    data = call.data
    question = QA[data]['question']
    answer = QA[data]['answer']

    # Форматируем ответ
    response = f"❓ <b>{question}</b>\n\n{answer}"

    # Отправляем ответ (используем parse_mode='HTML' для форматирования)
    bot.send_message(
        call.message.chat.id,
        response,
        parse_mode='HTML'
    )

    # Подтверждаем обработку callback
    bot.answer_callback_query(call.id)


# Модифицируем функцию создания кнопок (для динамического создания)
@bot.message_handler(commands=['QuesAns'])
def handle_helpcom(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Динамически создаем кнопки из словаря QA
    buttons = [
        types.InlineKeyboardButton(
            text=item['question'],
            callback_data=key
        ) for key, item in QA.items()
    ]

    markup.add(*buttons)
    bot.send_message(
        message.chat.id,
        "Часто задаваемые вопросы:",
        reply_markup=markup
    )

@bot.message_handler(commands=['start'])
def hand_start(message):
    bot.send_message(message.chat.id,
                     """Доброго времени суток! Я бот тех. поддержки магазина "Продаем всё на свете". Чтобы узнать список команд введите: /help""")


@bot.message_handler(commands=['help'])
def hand_helpcom(message):
    bot.send_message(message.chat.id, """Доступные команды:\n
    /QuesAns - ответы на часто задаваемые вопросы\n
    /probTech - сообщить о технической проблеме\n
    /probProd - сообщить о проблеме с продуктом\n
    /MyReq - просмотреть ваши запросы""")


def process_email(message):
    chat_id = message.chat.id
    email = message.text
    problem_data = user_data.get(chat_id, {})
    problem_desc = problem_data.get('problem')
    request_type = problem_data.get('type', 'tech')

    if not problem_desc:
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, начните заново.")
        return

    username = message.from_user.username or str(message.from_user.id)
    status = 'ждет рассмотрения'  # Новый статус
    logic.add_user(username, email, problem_desc, status)

    if chat_id in user_data:
        del user_data[chat_id]

    bot.send_message(chat_id, "✅ Ваш запрос успешно сохранен!")


def process_problem_description(message, request_type):
    chat_id = message.chat.id
    problem_desc = message.text
    user_data[chat_id] = {'problem': problem_desc, 'type': request_type}
    msg = bot.send_message(chat_id, "Теперь, пожалуйста, введите ваш email.")
    bot.register_next_step_handler(msg, process_email)  # Вызов process_email


@bot.message_handler(commands=['probTech'])
def hand_tecpr(message):
    msg = bot.send_message(message.chat.id, "Пожалуйста, опишите техническую проблему как можно подробнее.")
    bot.register_next_step_handler(msg, process_problem_description, 'tech')


@bot.message_handler(commands=['probProd'])
def hand_prodpr(message):
    msg = bot.send_message(message.chat.id, "Пожалуйста, опишите проблему с продуктом как можно подробнее.")
    bot.register_next_step_handler(msg, process_problem_description, 'prod')


def process_problem_description(message, request_type):
    chat_id = message.chat.id
    problem_desc = message.text
    user_data[chat_id] = {'problem': problem_desc, 'type': request_type}
    msg = bot.send_message(chat_id, "Теперь, пожалуйста, введите ваш email.")
    bot.register_next_step_handler(msg, process_email)


def process_email(message):
    chat_id = message.chat.id
    email = message.text
    problem_data = user_data.get(chat_id, {})
    problem_desc = problem_data.get('problem')
    request_type = problem_data.get('type', 'tech')

    if not problem_desc:
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, начните заново.")
        return

    username = message.from_user.username or str(message.from_user.id)
    status = 'Отправлено (тех.)' if request_type == 'tech' else 'Отправлено (прод.)'
    logic.add_user(username, email, problem_desc, status)

    if chat_id in user_data:
        del user_data[chat_id]

    bot.send_message(chat_id, "✅ Ваш запрос успешно сохранен!")

@bot.message_handler(commands=['MyReq'])
def handle_myreq(message):
    user_id = message.from_user.id
    requests = logic.get_user_requests(user_id)

    if not requests:
        bot.send_message(message.chat.id, "У вас нет активных запросов.")
        return

    response = "📝 Ваши последние запросы:\n\n"
    for req in requests:
        # Добавляем иконки для разных статусов
        status_icon = "🕒" if req['status'] == 'ждет рассмотрения' else "🔄" if req['status'] == 'рассматривается' else "✅"
        response += f"""📅 {req['created_at']}
{status_icon} Статус: {req['status']}
✉️ Сообщение: {req['request_text']}\n\n"""

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id, "Вы администратор!")
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")



if __name__ == "__main__":
    bot.polling(none_stop=True)