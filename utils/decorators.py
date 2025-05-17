from functools import wraps

from main import bot
from config import Config

def admin_only(func):
    """Декоратор для админских команд"""

    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.from_user.id in Config.ADMINS:  # Используем список из main.py
            return func(message, *args, **kwargs)
        bot.reply_to(message, "❌ | Требуются права администратора!")
        return None

    return wrapper


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
