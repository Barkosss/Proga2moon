# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import telebot
from telebot import types

from config import Config
from services.database import DataBase
from models.User import User
from enums.StatusEnum import Status

bot = telebot.TeleBot(Config.TOKEN)

# Создаем экземпляр базы данных
db = DataBase()


def register_command():
    from handlers import common, admin

    common.register_handlers(bot)
    #admin.register_handlers(bot)


@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем, есть ли пользователь в базе данных
    user_exists = db.has_user(message.from_user.id)

    if not user_exists:
        # Если пользователя нет, добавляем его
        new_user = User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        db.add_user(new_user)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    btn1 = types.KeyboardButton("Мой расписание")
    btn2 = types.KeyboardButton("Все мероприятия")
    btn3 = types.KeyboardButton("FQA")
    btn4 = types.KeyboardButton("Мой QR")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)


if __name__ == "__main__":
    register_command()
    print("Бот запущен")
    bot.polling(none_stop=True)
