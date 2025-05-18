import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional


@dataclass
class Workshop:
    """
    Сущность мастер-класса (Event):

    - id: UUID
    - event_id: UUID
    - title: название мероприятия
    - description: описание
    - location: место проведения (аудитория, комната, зал...)
    - start: время начала
    - end: время окончания
    - registration_required: нужна ли регистрация
    - speakers: список Telegram ID спикеров на мастер-классе
    - limited_capacity: ограничено ли число мест
    - capacity: число мест (если limited_capacity=True)
    - registered_user_ids: список ID зареганных участников
    - waiting_user_ids: список ID участников очереди
    - is_notified: флаг, который указывает, начался ли мастер-класс => сделали ли уведомления о начале
    """
    id: str
    event_id: int
    title: str
    description: str
    location: str
    start: datetime
    end: datetime
    registration_required: bool
    limited_capacity: bool
    is_notified: bool
    speakers: List[int]
    capacity: Optional[int] = None
    registered_user_ids: List[int] = field(default_factory=list)
    waiting_user_ids: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Workshop":
        return cls(
            id=str(uuid.uuid4()),
            event_id=data["event_id"],
            title=data["title"],
            description=data.get("description", ""),
            location=data.get("location", ""),
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            speakers=data.get("speakers", []),
            is_notified=data["is_notified"],
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
