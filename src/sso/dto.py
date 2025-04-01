from dataclasses import dataclass
from typing import Optional

from src.sso.models import User
from src.dto import BaseResponse


@dataclass
class LoginResponse(BaseResponse):
    result: bool = False


@dataclass
class GetMeResponse(BaseResponse):
    user: Optional[User] = None
