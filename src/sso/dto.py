from dataclasses import dataclass
from typing import Optional

from src.sso.models import User
from src.dto import BaseResponse, BoolResponse


@dataclass
class GetMeResponse(BaseResponse):
    user: Optional[User] = None


@dataclass
class RegisterResponse(BoolResponse):
    pass


@dataclass
class LoginResponse(BoolResponse):
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
class ChangePasswordResponse(BoolResponse):
    pass


@dataclass
class ChangeForgetPasswordResponse(BoolResponse):
    pass
