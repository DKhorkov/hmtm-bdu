from dataclasses import dataclass
from typing import Optional, List

from src.domains.sso.core.models import UserInfo
from src.domains.profile.core.schemas import Master
from src.core.common.dto import BoolResponse


@dataclass
class RegisterResponse(BoolResponse):
    display_name: Optional[str] = None
    email: Optional[str] = None


@dataclass
class LoginResponse(BoolResponse):
    email: Optional[str] = None


@dataclass
class ChangeForgetPasswordResponse(BoolResponse):
    pass


@dataclass
class VerifyEmailResponse(BoolResponse):
    pass


@dataclass
class SendVerifyEmailMessageResponse(BoolResponse):
    email: Optional[str] = None


@dataclass
class SendForgetPasswordMessageResponse(BoolResponse):
    pass


@dataclass
class GetFullUserInfoResponse:
    user: Optional[UserInfo] = None
    master: Optional[Master] = None
    errors: Optional[List[str]] = None
