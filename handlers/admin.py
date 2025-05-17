from utils.decorators import admin_only


def register_handlers(bot):

    @bot.message_handler(commands=['orders'])
    @admin_only
    def orders_by_user(message): # ПРИМЕР
        bot.reply_to(message, "Заявки участников")
