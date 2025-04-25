from config import bot
from telebot import types
import logic

hideBoard = types.ReplyKeyboardRemove()
user_data = {}


@bot.message_handler(commands=['QuesAns'])
def handle_helpcom(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("Как оформить заказ?", callback_data="question_order"),
        types.InlineKeyboardButton("Как узнать статус заказа?", callback_data="question_status"),
        types.InlineKeyboardButton("Как отменить заказ?", callback_data="question_cancel"),
        types.InlineKeyboardButton("Что делать, если товар пришел поврежденным?", callback_data="question_broke"),
        types.InlineKeyboardButton("Как связаться с вашей технической поддержкой?", callback_data="question_support"),
        types.InlineKeyboardButton("Как узнать информацию о доставке?", callback_data="question_delivery")
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Часто задаваемые вопросы:", reply_markup=markup)


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
        response += f"📅 {req['created_at']}\n🔧 Статус: {req['status']}\n✉️ Сообщение: {req['request_text']}\n\n"

    bot.send_message(message.chat.id, response)


if __name__ == "__main__":
    bot.polling(none_stop=True)