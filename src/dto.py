from dataclasses import dataclass, field
from typing import Dict, Optional, List

from src.cookies import CookiesConfig


@dataclass
class BaseResponse:
    headers: Optional[Dict[str, str]] = None
    cookies: List[CookiesConfig] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class BoolResponse(BaseResponse):
    result: bool = False
