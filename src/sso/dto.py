from dataclasses import dataclass, field
from typing import Optional, Dict, List
from src.cookies import CookiesConfig
from src.sso.models import User


@dataclass
class LoginResponse:
    result: bool = False
    headers: Optional[Dict[str, str]] = None
    cookies: List[CookiesConfig] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class GetMeResponse:
    user: Optional[User] = None
    error: Optional[str] = None
