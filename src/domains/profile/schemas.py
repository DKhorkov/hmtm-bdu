from typing import Optional, List

from pydantic import BaseModel

from src.core.common.cookies import CookiesConfig
from src.core.common.dto import User


class BaseResponse(BaseModel):
    error: Optional[str] = None
    cookies: List[CookiesConfig] = []


class Master(BaseModel):
    id: int
    info: Optional[str]
    created_at: str
    updated_at: str


class GetUserWithMasterResponse(BaseResponse):
    user: Optional[User] = None
    master: Optional[Master] = None
