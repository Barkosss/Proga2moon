from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import List, Optional


@dataclass
class User:
    """
    Сущность пользователя:

    - id: Telegram ID пользователя
    - first_name: имя
    - last_name: фамилия
    - patronymic: отчество (опционально)
    - birth_date: дата рождения (опционально)
    - registered_event_ids: список ID мероприятий, на которые пользователь зарегистрирован
    - queued_event_ids: список ID мероприятий, на которые пользователь стоит в очереди
    """
    id: int
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    birth_date: Optional[date] = None
    registered_event_ids: List[int] = field(default_factory=list)
    queued_event_ids: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        bd_raw = data.get("birth_date")
        birth_date = (
            datetime.fromisoformat(bd_raw).date()
            if isinstance(bd_raw, str)
            else bd_raw
        ) if bd_raw else None

        return cls(
            id=data["id"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            patronymic=data.get("patronymic"),
            birth_date=birth_date,
            registered_event_ids=data.get("registered_event_ids", []),
            queued_event_ids=data.get("queued_event_ids", []),
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.birth_date:
            data["birth_date"] = self.birth_date.isoformat()
        return data
