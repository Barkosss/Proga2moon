from functools import wraps

from main import bot
from config import Config

from services.database import DataBase as db

def admin_only_for(event_id: int):
    """Декоратор: проверка регистрации и прав на конкретный воркшоп"""
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            user = db.get_user(user_id)

            if not user:
                bot.send_message(
                    message.chat.id,
                    "🔒 | Вы не зарегистрированы. Сначала введите /registration_workshop"
                )
                return None

            if not db.workshop_access(user_id, event_id):
                bot.send_message(
                    message.chat.id,
                    f"❌ | У вас нет прав администратора на мероприятие #{event_id}"
                )
                return None

            return func(message, *args, **kwargs)
        return wrapper
    return decorator


def user_only(func):
    """Декоратор для зарегистрированных пользователей"""

    @wraps(func)
    # TODO: Сделать функцию проверки зарегистрированных пользователей
    def wrapper(message, *args, **kwargs):
        if bot.user_exists(message.from_user.id):  # Ваша функция проверки
            return func(message, *args, **kwargs)
        bot.reply_to(message, "🔐 | Сначала зарегистрируйтесь")
        return None

    return wrapper
