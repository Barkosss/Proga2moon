import telebot
from config import Config

from handlers.common import common_handler, register_callbacks
from handlers.admin import admin_handler
from enums.BotState import BotState

bot = telebot.TeleBot(Config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['is_admin'] = False

    bot.set_state(message.from_user.id, BotState.AWAIT_FIRST_NAME, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Добро пожаловать! Пожалуйста, введите ваше *имя*:",
        parse_mode='Markdown'
    )


@bot.message_handler(content_types=['text'])
def handler(message):
    user_id = message.from_user.id
    state = bot.get_state(user_id) or BotState.USER

    if state.startswith("BotState:AWAIT"):
        common_handler(bot, message, state)
        return

    with bot.retrieve_data(user_id) as data:
        is_admin = data.get('is_admin', False)

    if is_admin:
        admin_handler(bot, message, BotState.ADMIN)
    else:
        common_handler(bot, message, BotState.USER)


register_callbacks(bot)

if __name__ == "__main__":
    print("Bot is init")
    bot.polling(none_stop=True)
