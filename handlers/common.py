from utils.decorators import user_only

def register_handlers(bot):

    @bot.message_handler(commands=['help', 'start'])
    @user_only
    def send_welcome(message):
        bot.reply_to(message, """\
    Hi there, I am EchoBot.
    I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
    """)


    def handle_unknown(message):
        bot.reply_to(message, "Неправильный ввод!")

