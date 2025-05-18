from functools import wraps

from telebot.types import CallbackQuery

from main import bot
from models.Request import Request, Status
from services.database import DataBase as db


def admin_only(event_id: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(call: CallbackQuery, *args, **kwargs):
            event_request: Request = db.get_event(event_id)

            if event_request.status != Status.OK:
                bot.answer_callback_query(call.id, "❌ | Указанное мероприятие не найдено!")
                return

            is_admin = call.from_user.id in event_request.value.admin_ids
            if is_admin:
                return await func(call, *args, **kwargs)
            bot.answer_callback_query(call.id, "❌ Нужны права администратора!", show_alert=True)

        return wrapper

    return decorator


def user_only(func):
    """Декоратор для зарегистрированных пользователей"""

    @wraps(func)
    def wrapper(update, *args, **kwargs):
        user_id = update.message.from_user.id

        user_request: Request = db.get_user(user_id)

        if user_request.status != Status.OK:
            bot.reply_to(update, "🔐 | Сначала зарегистрируйтесь")
            return None

        return func(update, *args, **kwargs)

    return wrapper
