from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    display_name: str
    email: str
    email_confirmed: bool
    phone: Optional[str]
    phone_confirmed: bool
    telegram: Optional[str]
    telegram_confirmed: bool
    avatar: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class Master:
    id: int
    info: Optional[str]
    created_at: str
    updated_at: str
