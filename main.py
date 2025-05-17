import telebot

from config import Config

bot = telebot.TeleBot(Config.TOKEN)


def register_command():
    from handlers import common, admin

    common.register_handlers(bot)
    admin.register_handlers(bot)


if __name__ == "__main__":
    register_command()
    print("Bot is init")
    bot.polling(none_stop=True)
