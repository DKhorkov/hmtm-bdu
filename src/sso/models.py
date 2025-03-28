from dataclasses import dataclass
import datetime


@dataclass
class User:
    id: int
    email: str
    display_name: str
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = datetime.datetime.now()
