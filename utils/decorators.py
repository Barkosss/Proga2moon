from functools import wraps

from main import bot
from models.Request import Request, Status
from services.database import DataBase as db


def admin_only(func, event_id: int):
    """Декоратор для админских команд"""

    @wraps(func)
    def wrapper(message, *args, **kwargs):
        event_request: Request = db.get_event(event_id)

        if event_request.status != Status.OK:
            bot.reply_to(message, "❌ | Указанное мероприятие не найдено!")
            return None

        is_admin: bool = message.from_user.id in event_request.value.admins

        if is_admin:
            return func(message, *args, **kwargs)
        bot.reply_to(message, "❌ | Требуются права администратора!")
        return None

    return wrapper


def user_only(func):
    """Декоратор для зарегистрированных пользователей"""

    @wraps(func)
    # TODO: Сделать функцию проверки зарегистрированных пользователей
    def wrapper(message, *args, **kwargs):
        user_request: Request = db.get_user(message.from_user.id)
        if not (user_request.value is None):
            return func(message, *args, **kwargs)
        bot.reply_to(message, "🔐 | Сначала зарегистрируйтесь")
        return None

    return wrapper
