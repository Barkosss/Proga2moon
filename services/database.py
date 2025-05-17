import json
import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path

from models.User import User
from models.Workshop import Workshop


class FileData(Enum):
    """
    Перечисление для управления файлами данных в системе.
    Определяет стандартные файлы базы данных и их назначение.

    Attributes:
        USERS (str): Файл для хранения данных о пользователях.

        WORKSHOPS (str): Файл для хранения информации о воркшопах.
    """
    USERS = "users.json"
    WORKSHOPS = "workshops.json"


class DataBase:

    def _read_data(self, filename: FileData) -> None:
        """Прочитать JSON файл"""
        with open(f"../database/{filename.value}", "w") as file:
            self.data: dict = json.load(file)

    def _write_data(self, filename: FileData):
        """Записать новые данные в JSON файл"""

        file_path = Path(f"../database/{filename.value}")

        # Если файл не существует
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w") as file:
            json.dump(self.data, file, indent=4)

    def has_user(self, user_id: int) -> bool:
        """
        Проверить наличие пользователя среди зарегистрированных

        """
        self._read_data(FileData.USERS)
        return self.data[user_id]

    def get_user(self, user_id: int) -> User:
        """
        Получить пользователя по Telegram ID

        Args:
            user_id: Идентификатор пользователя для получения
        """
        self._read_data(FileData.USERS)
        return User.from_dict(self.data[user_id])

    def add_user(self, user: User):
        """
        Добавить нового пользователя

        Args:
            user: Объект пользователя для добавления
        """
        self.data[user.id] = user.to_dict()
        self._write_data(FileData.USERS)

    def get_workshop(self, workshop_id: int) -> Workshop:
        """
        Получить воркшоп по ID

        Args:
            workshop_id: Идентификатор воркщопа для получения
        """
        self._read_data(FileData.WORKSHOPS)
        return Workshop.from_dict(self.data[workshop_id])

    def get_workshops(self) -> list[Workshop]:
        """Получить список воркшопов"""
        self._read_data(FileData.WORKSHOPS)
        workshops: list[Workshop] = []

        for workshop_id in self.data[FileData.WORKSHOPS].keys():
            workshop: Workshop = self.get_workshop(workshop_id)
            workshops.append(workshop)

        return workshops

    def add_workshop(self, workshop: Workshop):
        """
        Добавить новый воркшоп

        Args:
            workshop: Объект вокршопа для добавления
        """
        self.data[workshop.id] = workshop.to_dict()
        self._write_data(FileData.WORKSHOPS)

    @staticmethod
    def create_backup():
        """Создать резервную копию"""
        backup_dir = Path("../database/backups")
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for file_type in FileData:
            src = Path(f"../database/{file_type.value}")
            dst = backup_dir / f"{timestamp}_{file_type.value}"
            shutil.copy2(src, dst)

    def load_backup(self):
        """Загрузить резервное копирование"""
        pass
