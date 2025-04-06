from dataclasses import dataclass
from typing import Optional

from src.sso.models import User
from src.dto import BaseResponse


@dataclass
class RegisterResponse(BaseResponse):
    result: bool = False


@dataclass
class LoginResponse(BaseResponse):
    result: bool = False


@dataclass
class VerifyEmailResponse(BaseResponse):
    result: bool = False


@dataclass
class SendVerifyEmailMessageResponse(BaseResponse):
    result: bool = False


@dataclass
class GetMeResponse(BaseResponse):
    user: Optional[User] = None


@dataclass
class SendForgetPasswordMessageResponse(BaseResponse):
    result: bool = False


@dataclass
class ChangePasswordResponse(BaseResponse):
    result: bool = False


@dataclass
class ChangeForgetPasswordResponse(BaseResponse):
    result: bool = False
