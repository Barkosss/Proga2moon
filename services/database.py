import json
from enum import Enum

from models import User, Workshop


class FileData(Enum):
    USERS = "users.json"
    WORKSHOPS = "workshops.json"


class DataBase:

    def _read_data(self, filename: FileData) -> None:
        """Прочитать JSON файл"""
        with open(f"../database/{filename.value}", "w") as file:
            self.data: dict = json.load(file)

    def _write_data(self, filename: FileData):
        """Записать новые данные в JSON файл"""
        with open(f"../database/{filename.value}", "w") as file:
            json.dump(self.data, file, indent=4)

    def has_user(self, user_id: int) -> bool:
        """Проверить наличие пользователя среди зарегистрированных"""
        self._read_data(FileData.USERS)
        return self.data[user_id]

    def get_user(self, user_id: int) -> User:
        """Получить пользователя по Telegram ID"""
        self._read_data(FileData.USERS)
        return self.data[user_id]

    def add_user(self, user: User):
        """Добавить нового пользователя"""
        self.data[user.id] = user.to_json()
        self._write_data(FileData.USERS)

    def get_workshop(self, workshop_id: int) -> Workshop:
        """Получить воркшоп по ID"""
        pass

    def add_workshop(self, workshop: Workshop):
        """Добавить новый воркшоп"""
        pass

    def create_backup(self):
        """Создать резервную копию"""
        pass

    def load_backup(self):
        """Загрузить резервное копирование"""
        pass
