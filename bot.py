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

if __name__ == "__main__":
    bot.polling(none_stop=True)