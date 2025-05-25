from dataclasses import dataclass
from typing import Optional, List, Dict

from src.sso.models import User, Master, UserInfo, Toy, ToysFilters
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
class GetFullUserInfoResponse:
    user: Optional[UserInfo] = None
    master: Optional[Master] = None
    errors: Optional[List[str]] = None


@dataclass
class ToysCategoriesResponse:
    categories: Optional[Dict[str, int | str]] = None


@dataclass
class ToysTagsResponse:
    tags: Optional[Dict[str, int | str]] = None


@dataclass
class ToysCatalogResponse(ToysCategoriesResponse, ToysTagsResponse):
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    toys: Optional[List[Toy]] = None
    error: Optional[str] = None
    filters: Optional[ToysFilters] = None


@dataclass
class ToyByIDResponse(BoolResponse):
    toy: Optional[Toy] = None
