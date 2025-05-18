import re
from datetime import datetime

from enums.StatusEnum import Status
from models.Request import Request

def validate_birthday(birthday: str) -> Request:
    """
    Валидация дня рождения

    :arg
        birthday - дата рождения

    :return
        Request - в поле value хранится True, если дата валидна, иначе False
    """
    try:
        datetime.strptime(birthday, "%d.%m.%Y")
        return Request(status=Status.OK, value=True)
    except ValueError:
        return Request(status=Status.ERROR, value=False)

def validate_phone(phone: str) -> Request:
    """
    Валидация номера телефона

    :arg
        phone - номер телефона

    :return
        Request - в поле value хранится True или False
    """
    if not re.match(r'^\+?[1-9]\d{10,14}$', phone):
        return Request(status=Status.OK, value=False)