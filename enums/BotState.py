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

    AWAIT_EVENT_TITLE = State()
    AWAIT_EVENT_DESC = State()
    AWAIT_EVENT_START = State()
    AWAIT_EVENT_END = State()
    AWAIT_EVENT_LOCATION = State()
    AWAIT_EVENT_CHAT = State()

    AWAIT_NEW_EVENT_TITLE = State()
    AWAIT_NEW_EVENT_DESC = State()
    AWAIT_NEW_EVENT_DATE_START = State()
    AWAIT_NEW_EVENT_DATE_END = State()
    AWAIT_NEW_EVENT_LOCATION = State()
    AWAIT_NEW_EVENT_CHAT_LINK = State()

    AWAIT_NEW_WORKSHOP_TITLE = State()
    AWAIT_NEW_WORKSHOP_CAPACITY = State()

    AWAIT_ADMIN_ANSWER = State()
    AWAIT_ADMIN_CONFIRMATION = State()

