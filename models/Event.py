from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Event:
    """
    Сущность «Мероприятие» — контейнер для мастер-классов.

    Поля:
    - id: UUID
    - start: время начала мероприятия
    - end: время окончания мероприятия
    - workshop_ids: список ID мастер-классов, принадлежащих этому событию
    - admin_ids: список Telegram ID организаторов/админов
    """
    id: str
    start: datetime
    end: datetime
    workshop_ids: List[str] = field(default_factory=list)
    admin_ids: List[int] = field(default_factory=list)

    @classmethod
    def create_new(cls,
                   start: datetime,
                   end: datetime,
                   admin_ids: Optional[List[int]] = None,
                   ) -> "Event":
        return cls(
            id=str(uuid.uuid4()),
            workshop_ids=[],
            admin_ids=admin_ids or [],
            start=start,
            end=end
        )

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        return cls(
            id=d["id"],
            workshop_ids=d.get("workshop_ids", []),
            admin_ids=d.get("admin_ids", []),
            start=datetime.fromisoformat(d["start"]),
            end=datetime.fromisoformat(d["end"]),
        )

    def to_dict(self) -> dict:
        out = asdict(self)
        out["start"] = self.start.isoformat()
        out["end"] = self.end.isoformat()
        return out

    def add_workshop(self, workshop_id: str) -> None:
        if workshop_id not in self.workshop_ids:
            self.workshop_ids.append(workshop_id)

    def remove_workshop(self, workshops_id: str) -> None:
        self.workshop_ids = [w for w in self.workshop_ids if w != workshops_id]

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids

    @property
    def duration_hours(self) -> float:
        delta = self.end - self.start
        return delta.total_seconds() / 3600
