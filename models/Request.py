from enum import Enum

from pydantic import BaseModel


class Status(Enum):
    """
    ...
    """
    OK = "OK"
    ERROR = "ERROR"
    WARNING = "WARNING"


class Request(BaseModel):
    status: Status
    value = None
    message: str | None = None
