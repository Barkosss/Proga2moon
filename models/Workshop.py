from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Union


@dataclass
class Workshop:
    """
    Сущность мастер-класса (Event):

    - id: UUID или целочисленный счётчик (ID мастер класса внутри мероприятия)
    - event_id: UUID или целочисленный счётчик (ID глобального мероприятия)
    - title: название мероприятия
    - description: описание
    - start: время начала (ISO-строка → datetime)
    - end: время окончания
    - registration_required: нужна ли регистрация
    - limited_capacity: ограничено ли число мест
    - capacity: число мест (если limited_capacity=True)
    - registered_user_ids: список ID зареганных участников
    - waiting_user_ids: список ID участников очереди
    """
    id: int
    event_id: int
    title: str
    description: str
    start: datetime
    end: datetime
    registration_required: bool
    limited_capacity: bool
    capacity: Optional[int] = None
    registered_user_ids: List[Union[int, str]] = field(default_factory=list)
    waiting_user_ids: List[Union[int, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Workshop":
        return cls(
            id=data["id"],
            event_id=data["event_id"],
            title=data["title"],
            description=data.get("description", ""),
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            registration_required=bool(data.get("registration_required", False)),
            limited_capacity=bool(data.get("limited_capacity", False)),
            capacity=data.get("capacity"),
            registered_user_ids=data.get("registered_user_ids", []),
            waiting_user_ids=data.get("waiting_user_ids", []),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["start"] = self.start.isoformat()
        d["end"] = self.end.isoformat()
        return d
