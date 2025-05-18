from functools import wraps
from services.database import DataBase
db = DataBase()
from main import bot
from models.Request import Request, Status
from services.database import DataBase
db = DataBase()


def admin_only(event_id: int):
    """
    Декоратор для админских команд на конкретное мероприятие.

    Проверяет, является ли пользователь админом указанного мероприятия.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            event_request: Request = db.get_event(event_id)

            if event_request.status != Status.OK:
                bot.reply_to(message, "❌ | Указанное мероприятие не найдено!")
                return

            event = event_request.value

            if message.from_user.id in event.admin_ids:
                return func(message, *args, **kwargs)

            bot.reply_to(message, "❌ | Требуются права администратора!")
            return

        return wrapper

    return decorator

def admin_only_event_callback(func):
    """
    Декоратор для callback-функций, проверяющий, имеет ли пользователь доступ к редактированию event.
    Предполагает, что в callback_data передано "event_edit:<event_id>"
    """
    @wraps(func)
    def wrapper(call, *args, **kwargs):
        try:
            event_id = int(call.data.split(":")[1])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "❌ Некорректный запрос.")
            return

        user_id = call.from_user.id
        events = db.get_admin_events(user_id)
        if not any(e.id == event_id for e in events):
            bot.answer_callback_query(call.id, "❌ У вас нет доступа к этому мероприятию.")
            return

        return func(call, event_id=event_id, *args, **kwargs)
    return wrapper

def user_only(func):
    """
    Декоратор для команд, доступных только зарегистрированным пользователям.
    Если пользователь не найден в базе данных, бот отвечает предупреждением.
    """
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_request: Request = db.get_user(message.from_user.id)
        if user_request.status == Status.OK:
            return func(message, *args, **kwargs)
        else:
            bot.reply_to(message, "🔐 | Сначала зарегистрируйтесь")
            return None
    return wrapper