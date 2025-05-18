from telebot import TeleBot
from telebot.types import Message

from enums.CommandsEnum import Commands


def admin_handler(bot: TeleBot, message: Message, state):
    try:
        command: Commands.AdminEnum = Commands.AdminEnum(message.text)
        with bot.retrieve_data(message.from_user.id) as data:
            data['is_admin'] = True

        match command:
            case Commands.AdminEnum.EDIT: edit()
    except ValueError as err:
        print("")

def edit():
    print("Edit")


def register_handlers(bot):
    @bot.message_handler(commands=['orders'])
    #@admin_only
    def orders_by_user(message):  # ПРИМЕР
        bot.reply_to(message, "Заявки участников")

    @bot.message_handler(content_types=['text'])
    def handler(message):
        print(message.text)
        command = Commands.AdminEnum(message.text)
        match command:
            case Commands.AdminEnum.EDIT: edit()
