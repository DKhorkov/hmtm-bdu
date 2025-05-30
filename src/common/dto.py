from dataclasses import dataclass, field
from typing import Optional, Dict, List

from src.common.cookies import CookiesConfig
from src.common.models import User


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
