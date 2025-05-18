import telebot
from telebot import types

from config import Config
from handlers.admin import admin_handler
from handlers.common import common_handler
from enums.CommandsEnum import Commands
from enums.BotState import BotState

bot = telebot.TeleBot(Config.TOKEN)


def register_command():
    from handlers import common, admin

    common.register_handlers(bot)
    admin.register_handlers(bot)


@bot.message_handler(content_types=['text'])
def handler(message):
    user_id = message.from_user.id
    current_state = bot.get_state(user_id)

    if current_state and current_state.startswith("BotState:AWAIT"):
        with bot.retrieve_data(message.from_user.id) as data:
            if bool(data['is_admin']):
                admin_handler(bot, message, current_state)
            else:
                common_handler(bot, message, current_state)

    with bot.retrieve_data(message.from_user.id) as data:
        if bool(data['is_admin']):
            admin_handler(bot, message, BotState.ADMIN)
        else:
            common_handler(bot, message, BotState.USER)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(types.KeyboardButton(Commands.CommonEnum.MY_SCHEDULE.value),
               types.KeyboardButton(Commands.CommonEnum.ALL_EVENTS.value),
               types.KeyboardButton(Commands.CommonEnum.FAQ.value),
               types.KeyboardButton(Commands.CommonEnum.MY_QR.value))

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


if __name__ == "__main__":
    register_command()
    print("Bot is init")
    bot.polling(none_stop=True)
