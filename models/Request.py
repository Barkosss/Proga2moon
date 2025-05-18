from pydantic import BaseModel
from enums.StatusEnum import Status

class Request(BaseModel):
    status: Status
    value: object = None
    message: str | None = None
