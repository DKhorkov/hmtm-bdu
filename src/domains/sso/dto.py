from dataclasses import dataclass
from typing import Optional, List

from src.domains.sso.models import UserInfo
from src.domains.profile.models import Master
from src.core.common.dto import BoolResponse


@dataclass
class RegisterResponse(BoolResponse):
    pass


@dataclass
class LoginResponse(BoolResponse):
    pass


@dataclass
class ChangeForgetPasswordResponse(BoolResponse):
    pass


@dataclass
class VerifyEmailResponse(BoolResponse):
    pass


@dataclass
class SendVerifyEmailMessageResponse(BoolResponse):
    pass


@dataclass
class SendForgetPasswordMessageResponse(BoolResponse):
    pass


@dataclass
class GetFullUserInfoResponse:
    user: Optional[UserInfo] = None
    master: Optional[Master] = None
    errors: Optional[List[str]] = None
