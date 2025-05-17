from utils.decorators import user_only

def register_handlers(bot):

    @bot.message_handler(commands=["start", "help"])
    # @user_only - доступен только зарегистрированным пользователям
    def handle_start(message):
        bot.reply_to(message, "Welcome!")
