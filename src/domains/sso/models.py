from dataclasses import dataclass
from typing import Optional


@dataclass
class UserInfo:
    id: str
    display_name: str
    email: str
    phone: Optional[str]
    telegram: Optional[str]
    avatar: Optional[str]
    created_at: str
