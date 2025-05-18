from enum import StrEnum


class Commands:
    """
    Перечисление наименований встроенных и неизменяемых кнопок бота
    Используется для строгой типизации текстовых команд.
    """

    class CommonEnum(StrEnum):
        MY_SCHEDULE = "Моё расписание"
        ALL_EVENTS = "Все мероприятия"
        FAQ = "FAQ"
        MY_QR = "Мой QR"
        REGISTRATION = "Зарегистрироваться"
        AWAIT_MODE = "Режим ожидания"
        CANCEL_REGISTRATION = "Отменить регистрацию"
        QUIT_AWAIT_MODE = "Выйти из режима ожидания"
        YES = "Да"
        NO = "Нет"
        SELECT_EVENT = "Выбрать мероприятие"

    class AdminEnum(StrEnum):
        ANSWER = "Ответить"
        SEND = "Отправить"
        EDIT = "Редактировать"
        CHANGE = "Изменить"
        QUESTIONS_BY_USERS = "Вопросы от участников"
        BECOME_TO_USER = "Стать обычным пользователем"
        MANAGE_ADMINS = "Управление админами"
        MANAGE_WORKSHOPS = "Управление мастерклассами"
        MANAGE_EVENT = "Управление мероприятием"
