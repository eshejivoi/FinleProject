from config import TOKEN
import telebot


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def hand_start(message):
    bot.send_message(message.chat.id,"""Доброго времени суток! Я бот тех. поддержки магазина "Продаем всё на свете". Чтобы узнать список комманд введите: /help""")

@bot.message_handler(commands=['help'])
def hand_helpcom(message):
    bot.send_message(message.chat.id, """доступные команды: \n
    /QuesAns - ответы на часто задаваемые вопросы \n
    /probTech - отправить запрос программисту если вы заметили что сайт не работает \n
    /probProd - отправить запрос продавцу насчет продукта который вы хотели/хотите или уже купили""")