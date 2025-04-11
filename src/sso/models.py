from dataclasses import dataclass


@dataclass
class User:
    id: int
    display_name: str
    email: str
    email_confirmed: bool
    phone: str
    phone_confirmed: bool
    telegram: str
    telegram_confirmed: bool
    avatar: str
    created_at: str
    updated_at: str
