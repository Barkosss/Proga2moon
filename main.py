import telebot

from handlers.common import handler_common_command

bot = telebot.TeleBot("7604836846:AAHu90C0unNVMEYd442FsGzTQSRpYGjzxaU")
print("Bot is init")


@bot.message_handler(func=lambda message: True)
def get_message(message):
    text = message.text
    if text.startswith('/'):
        arguments = text.split(" ")
        command = arguments[0][1:].split('@')[0].lower()
        arguments = [arg for arg in arguments[1:] if len(arg)]
        handler_common_command(command, arguments)


bot.infinity_polling()
