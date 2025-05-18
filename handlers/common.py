from telebot import TeleBot
from telebot.types import Message

from enums.CommandsEnum import Commands


def common_handler(bot: TeleBot, message: Message, state):
    try:
        command: Commands.AdminEnum = Commands.AdminEnum(message.text)
        with bot.retrieve_data(message.from_user.id) as data:
            data['is_admin'] = False

        match command:
            case Commands.AdminEnum.EDIT: edit()
    except ValueError as err:
        print(f"Command {message.text} is not a valid command")


def edit():
    print("Edit")


def register_handlers(bot):
    # @user_only
    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        bot.reply_to(message, """\
    Hi there, I am EchoBot.
    I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
    """)

    # @user_only
    @bot.message_handler(content_types=["text"])
    def handle_unknown(message):
        bot.reply_to(message, "Неправильный ввод!")
