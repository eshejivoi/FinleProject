from config import bot  # Импортируем созданный в config.py бот
from telebot import types
import logic
hideBoard = types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def hand_start(message):
    bot.send_message(message.chat.id,"""Доброго времени суток! Я бот тех. поддержки магазина "Продаем всё на свете". Чтобы узнать список комманд введите: /help""")

@bot.message_handler(commands=['help'])
def hand_helpcom(message):
    bot.send_message(message.chat.id, """доступные команды: \n
    /QuesAns - ответы на часто задаваемые вопросы \n
    /probTech - отправить запрос программисту если вы заметили что сайт не работает \n
    /probProd - отправить запрос продавцу насчет продукта который вы хотели/хотите или уже купили""")


@bot.message_handler(commands=['QuesAns'])
def handle_helpcom(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Создаем кнопки с уникальными callback_data
    button1 = types.InlineKeyboardButton(
        "Как оформить заказ?",
        callback_data="question_order"
    )
    button2 = types.InlineKeyboardButton(
        "Как узнать статус заказа?",
        callback_data="question_status"
    )
    button3 = types.InlineKeyboardButton(
        "Как отменить заказ?",
        callback_data="question_cancel"
    )
    button4 = types.InlineKeyboardButton(
            "Что делать, если товар пришел поврежденным?",
        callback_data="question_broke"
    )
    button5 = types.InlineKeyboardButton(
        "Как связаться с вашей технической поддержкой?",
        callback_data="question_support"
    )
    button6 = types.InlineKeyboardButton(
        "Как узнать информацию о доставке?",
        callback_data="question_delivery"
    )

    markup.add(button1, button2, button3, button4, button5, button6)
    bot.send_message(message.chat.id, "Часто задаваемые вопросы:", reply_markup=markup)



@bot.message_handler(commands=['probTech'])
def hand_tecpr(message):
    msg = bot.send_message(message.chat.id,
                            "Пожалуйста, опишите проблему как можно подробнее. Наши разработчики уже уведомлены и скоро её исправят.",
                            reply_markup=hideBoard)
    bot.register_next_step_handler(msg, process_tech_request)


def process_tech_request(message):
    user_id = message.from_user.id
    username = message.from_user.username
    request_text = message.text

    # Сохраняем запрос в базу
    logic.save_tech_request(user_id, username, request_text)
    bot.send_message(message.chat.id, "✅ Ваш запрос успешно сохранен!")

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