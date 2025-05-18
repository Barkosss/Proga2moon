import telebot
from telebot import types

from config import Config

bot = telebot.TeleBot(Config.TOKEN)


def register_command():
    from handlers import common, admin

    common.register_handlers(bot)
    admin.register_handlers(bot)

def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("Кнопка 1")
    btn2 = types.KeyboardButton("Кнопка 2")

    markup.row(btn1, btn2)


@bot.message_handler(commands=["start"])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("Мои мероприятия")
    btn2 = types.KeyboardButton("Вопросы от участников")
    btn3 = types.KeyboardButton("Меню")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Привет, выбери действие:", reply_markup=markup)



if __name__ == "__main__":
    register_command()
    print("Bot is init")
    bot.polling(none_stop=True)

