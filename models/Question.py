@dataclass
class Question:
    id: str
    event_id: int
    user_id: int
    text: str
    created_at: datetime
