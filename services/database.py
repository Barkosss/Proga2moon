import json
import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path

from models import *


class FileData(Enum):
    """
    Перечисление для управления файлами данных в системе.
    Определяет стандартные файлы базы данных и их назначение.

    Attributes:
        USERS (str): Файл для хранения данных о пользователях.
        WORKSHOPS (str): Файл для хранения информации о воркшопах.
        EVENTS (str): Файл для хранения информации об ивентах
    """
    USERS = "users.json"
    WORKSHOPS = "workshops.json"
    EVENTS = "event.json"
    QUESTIONS = "questions.json"


# TODO: Подумать и добавить работу с таблицей вопросов
class DataBase:
    """
    Класс для работы с локальной JSON-базой данных, хранящей информацию о пользователях и воркшопах.

    Attributes:
        data (dict): Временная структура данных, загружаемая из JSON-файлов.

    Methods:
        _read_data(): Приватный метод для чтения данных из JSON-файла.
        _write_data(): Приватный метод для записи данных в JSON-файл.
        has_user(telegram_id): Проверяет наличие пользователя по Telegram ID.
        get_user(telegram_id): Получает объект пользователя по Telegram ID.
        add_user(user_data): Добавляет нового пользователя в базу данных.
        get_workshop(workshop_id): Получает воркшоп по его уникальному идентификатору.
        get_workshops(): Возвращает список всех доступных воркшопов.
        add_workshop(workshop_data): Добавляет новый воркшоп в базу данных.
        create_backup(): Создаёт резервную копию текущих данных.
        load_backup(): Восстанавливает данные из ранее созданной резервной копии.
    """

    def _read_data(self, filename: FileData) -> None:
        """Прочитать JSON файл"""
        with open(f"../database/{filename.value}", "w") as file:
            self.data: dict = json.load(file)

    def _write_data(self, filename: FileData) -> None:
        """Записать новые данные в JSON файл"""

        file_path = Path(f"../database/{filename.value}")

        # Если файл не существует
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w") as file:
            json.dump(self.data, file, indent=4)

    def has_user(self, user_id: int) -> Request:
        """
        Проверить наличие пользователя среди зарегистрированных
        """
        try:
            self._read_data(FileData.USERS)
            return Request(status=Status.OK, value=self.data[user_id])
        except KeyError as err:
            return Request(status=Status.ERROR, message=f"User by id({user_id}) not found: {err}", value=False)

    def get_user(self, user_id: int) -> Request:
        """
        Получить пользователя по Telegram ID

        Args:
            user_id: Идентификатор пользователя для получения
        """
        self._read_data(FileData.USERS)
        try:
            return Request(status=Status.OK, value=User.from_dict(self.data[user_id]))
        except KeyError as err:
            return Request(status=Status.ERROR, message=f"Couldn't get the user: {err}")

    def add_user(self, user: User) -> Request:
        """
        Добавить нового пользователя

        Args:
            user: Объект пользователя для добавления
        """
        try:
            self.data[user.id] = user.to_dict()
            self._write_data(FileData.USERS)
            return Request(status=Status.OK)
        except KeyError as err:
            return Request(status=Status.ERROR, message=f"Couldn't add a new user: {err}")

    def get_workshop(self, workshop_id: str) -> Request:
        """
        Получить воркшоп по ID

        Args:
            :param workshop_id: Идентификатор воркшопа для получения
        """
        self._read_data(FileData.WORKSHOPS)
        try:
            return Request(status=Status.OK, value=Workshop.from_dict(self.data[workshop_id]))
        except KeyError as err:
            return Request(status=Status.ERROR, message=f"Couldn't get the workshop: {err}", value=False)

    def get_workshops(self) -> Request:
        """
        Получить список воркшопов
        """
        self._read_data(FileData.WORKSHOPS)

        workshops: list[Workshop] = list[Workshop]()

        try:
            for workshop_id in self.data.keys():
                workshop_request: Request = self.get_workshop(workshop_id)
                if workshop_request.status == Status.OK:
                    workshops.append(workshop_request.value)

            return Request(status=Status.OK, value=workshops)
        except KeyError as err:
            return Request(status=Status.ERROR,
                           message=f"Couldn't get all the workshops: {err}", value=False)

    def set_workshop_notify(self, workshop_id: str, is_notify: bool) -> Request:
        """
        Установить флаг с оповещением

        Args:
              workshop_id - Идентификатор воркшопа
              is_notify - Флаг, отправили ли оповещение или нет
        """
        self._read_data(FileData.WORKSHOPS)

        if workshop_id in self.data.keys():
            return Request(status=Status.ERROR, message="")

        workshop_request: Request = self.get_workshop(workshop_id)
        workshop: Workshop = Workshop.from_dict(workshop_request.value)
        workshop.is_notified = is_notify

        self.data[workshop_id] = workshop.to_dict()

        self._write_data(FileData.WORKSHOPS)
        return Request(status=Status.OK, value=workshop)

    def get_event_workshops(self, event_id: int) -> Request:
        """
        Получить список воркшопов у определённого ивента

        Args:
            event_id: Идентификатор ивента
        """
        self._read_data(FileData.EVENTS)

        if self.data.get(event_id) is None:
            return Request(status=Status.ERROR, message=f"An event by id({event_id}) is not found", value=False)

        event: Event = self.data[event_id]
        workshops: list[Workshop] = []

        try:
            for workshop_id in event.workshop_ids:
                workshop_request: Request = self.get_workshop(workshop_id)
                if workshop_request.status == Status.OK:
                    workshops.append(workshop_request.value)

            return Request(status=Status.OK, value=workshops)
        except KeyError as err:
            return Request(status=Status.ERROR,
                           message=f"Couldn't get all the workshops from event ({event_id}): {err}", value=False)

    def add_workshop(self, event_id: int, workshop: Workshop) -> Request:
        """
        Добавить новый воркшоп

        Args:
            event_id: Идентификатор ивента
            workshop: Объект вокршопа для добавления
        """
        self._read_data(FileData.EVENTS)

        if not (event_id in self.data.keys()):
            return Request(status=Status.ERROR, message="Event id is not found", value=False)

        event: Event = Event.from_dict(self.data[event_id])
        event.workshop_ids.append(workshop.id)

        try:
            self.data[event.id] = event.to_dict()
            self._write_data(FileData.EVENTS)
            return Request(status=Status.OK)
        except KeyError as err:
            return Request(status=Status.ERROR,
                           message=f"Couldn't add a new workshop ({workshop.id}) to event ({event_id}): {err}",
                           value=False)

    def get_event(self, event_id: int) -> Request:
        """
        Получить ивент

        Args:
            event_id: Идентификатор ивента
        """
        self._read_data(FileData.EVENTS)

        if self.data.get(event_id) is None:
            return Request(status=Status.ERROR, message=f"An event by id({event_id}) is not found", value=False)

        event: Event = self.data[event_id]
        return Request(status=Status.OK, value=event.to_dict())

    def get_events(self) -> Request:
        """
        Получить ивенты
        """
        self._read_data(FileData.EVENTS)

        events: list[Event] = []
        for event_id in self.data.keys():
            events.append(self.data[event_id].to_dict())

        return Request(status=Status.OK, value=events)

    def add_event(self, event: Event, workshops: list[Workshop]) -> Request:
        """
        Добавить новый ивент

        Args:
            event: Объект ивента
            workshops: Список воркшопов
        """
        try:
            self._read_data(FileData.EVENTS)

            if not (self.data.get(event.id) is None):
                return Request(status=Status.ERROR, message=f"An event by id({event.id}) is not found", value=False)

            for workshop in workshops:
                if workshop.id not in event.workshop_ids:
                    event.workshop_ids.append(workshop.id)

            self._write_data(FileData.EVENTS)
        except KeyError as err:
            return Request(status=Status.ERROR, message=f"An event by id({event.id}) or workshop is not found: {err}")

        try:
            self._read_data(FileData.WORKSHOPS)

            for workshop in workshops:
                self.data[workshop.id] = workshop.to_dict()

            self._write_data(FileData.WORKSHOPS)
            return Request(status=Status.OK)
        except KeyError as err:
            return Request(status=Status.ERROR, message=f"A workshop is not found: {err}")

    @staticmethod
    def create_backup():
        """Создать резервную копию"""
        backup_dir = Path("../database/backups")
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for file_type in FileData:
            source = Path(f"../database/{file_type.value}")
            backup = backup_dir / f"{timestamp}_{file_type.value}"
            shutil.copy2(source, backup)

    @staticmethod
    def load_backup(backup_name: str = None):
        """
        Загрузить резервную копию

        Args:
            backup_name: Имя папки с бэкапом (формат YYYYMMDD_HHMMSS)
                      Если None, загрузит последний доступный бэкап

        Returns:
            bool: True если восстановление прошло успешно
        """

        pass
