from telebot.states import StatesGroup, State


class BotState(StatesGroup):
    USER = State()
    ADMIN = State()

    # Регистрация пользователя
    AWAIT_NAME = State()
    AWAIT_BIRTHDATE = State()
    AWAIT_CONTACT = State()

    # Создание/редактирование мероприятия
    AWAIT_EVENT_TITLE = State()
    AWAIT_EVENT_TIME = State()
    AWAIT_CHAT_LINK = State()

    # Мастер-классы
    AWAIT_WORKSHOP_TITLE = State()
    AWAIT_WORKSHOP_TIME = State()
