from utils.decorators import admin_only_for


def register_handlers(bot):
    @bot.message_handler(commands=['check_user'])
    @admin_only_for(event_id=100)
    def check_user(message):
        bot.reply_to(message, "Заявки участников")

    @bot.message_handler(commands=["create_workshop"])
    @admin_only_for(event_id=100)
    def create_workshop(message):
        msg = bot.send_message(message.chat.id, "Введите название воркшопа:")
        bot.register_next_step_handler(msg, get_title)

    @bot.message_handler(commands=["edit_workshop"])
    @admin_only_for(event_id=1)
    def edit_workshop(message):
        pass
        # показываем inline-кнопки для изменения title, desc, time, limit

    @bot.message_handler(commands=["remove_workshop"])
    @admin_only_for(event_id=1)
    def remove_workshop(message):
        pass
    # подтверждение через кнопку или просто удалить и ответить

