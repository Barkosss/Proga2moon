from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Question:
    id: str
    event_id: int
    user_id: int
    text: str
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        return cls(
            id=data["id"],
            event_id=data["event_id"],
            user_id=data["user_id"],
            text=data["text"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d
