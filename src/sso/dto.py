from dataclasses import dataclass
from typing import Optional, List

from src.sso.models import User, Master, UserInfo
from src.dto import BaseResponse, BoolResponse


@dataclass
class GetMeResponse(BaseResponse):
    user: Optional[User] = None


@dataclass
class UpdateUserProfileResponse(BoolResponse):
    pass


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


@dataclass
class RefreshTokensResponse(BoolResponse):
    pass


@dataclass
class GetUserIsMasterResponse(BoolResponse):
    master: Optional[Master] = None


@dataclass
class UpdateMasterResponse(BoolResponse):
    pass


@dataclass
class RegisterMasterResponse(BoolResponse):
    pass


@dataclass
class GetAllUserInfoResponse:
    user: Optional[UserInfo] = None
    master: Optional[Master] = None
    errors: Optional[List[str]] = None
