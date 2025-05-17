import os

import cv2
import segno
from qreader import QReader

from services.database import DataBase


class Security:
    db = DataBase()
    PATH_QRCodes = "../QRCodes/"

    @staticmethod
    def create_qr(user_id: int = 10) -> str:
        """
        Создаёт QR-код на основе идентификатора пользователя и сохраняет его в виде изображения.

        Args:
            user_id (int): Идентификатор пользователя (Telegram ID). По умолчанию 10.

        Returns:
            str: Полный путь к сохранённому файлу с QR-кодом.
        """
        qrcode = segno.make_qr(user_id)
        path = Security.PATH_QRCodes + f"{user_id}.png"
        os.makedirs(Security.PATH_QRCodes, exist_ok=True)
        qrcode.save(path)
        return path

    @staticmethod
    def check_qr(file_name: str, event_id: int) -> bool:
        """
        Проверить QR код

        Args:
            file_name: Название файла с QR кодом

            event_id: ID воркшопа

        Returns:
            True, если пользователь зарегистрирован на данное мероприятие, иначе False
        """
        qreader = QReader()
        user_id: int
        try:
            path = Security.PATH_QRCodes + f"{file_name}.png"
            image = cv2.imread(path)
            decoded_texts: tuple = qreader.detect_and_decode(image=image)
            user_id = int(decoded_texts[0])
            # TODO: Добавить более понятную ошибку, почему False
        except Exception:
            return False

        workshop = Security.db.get_workshop(event_id)
        return workshop.registered_user_ids.get[user_id]