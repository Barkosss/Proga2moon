from utils.decorators import user_only

def register_handlers(bot):

    @bot.message_handler(commands=["start", "help"])
    def handle_start(message):
        bot.reply_to(message, "Welcome!")
