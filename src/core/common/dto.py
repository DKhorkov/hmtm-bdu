from dataclasses import dataclass, field
from typing import Optional, Dict, List

from src.core.cookies.schemas import CookiesConfig


@dataclass
class User:
    id: str
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
class BaseResponse:
    headers: Optional[Dict[str, str]] = None
    cookies: List[CookiesConfig] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class GetMeResponse(BaseResponse):
    user: Optional[User] = None


@dataclass
class BoolResponse(BaseResponse):
    result: bool = False


@dataclass
class RefreshTokensResponse(BoolResponse):
    pass
