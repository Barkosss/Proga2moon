from enum import StrEnum

class BotState(StrEnum):
    USER = "BotState:USER"
    ADMIN = "BotState:ADMIN"
    AWAIT_FIRST_NAME = "BotState:AWAIT_FIRST_NAME"
    AWAIT_LAST_NAME = "BotState:AWAIT_LAST_NAME"
    AWAIT_PATRONYMIC = "BotState:AWAIT_PATRONYMIC"
    AWAIT_BIRTH_DATE = "BotState:AWAIT_BIRTH_DATE"
