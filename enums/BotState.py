from telebot.states import StatesGroup, State


class BotState(StatesGroup):
    USER = State()
    ADMIN = State()
    AWAIT_NAME = State()
    AWAIT_BIRTHDATE = State()
    AWAIT_CONTACT = State()