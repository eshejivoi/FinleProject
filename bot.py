from config import TOKEN
import telebot


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def hand_start(message):
    bot.send_message(message.chat.id,"Доброго времени суток! Я бот тех. поддержки. Чтобы узнать список комманд введите: /help")