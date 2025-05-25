from typing import Dict, Optional, BinaryIO, Union, List
from pydantic import EmailStr
from dataclasses import dataclass

from src.sso.models import ToysFilters


@dataclass(frozen=True)
class RegisterUserVariables:
    display_name: str
    email: str
    password: str

    def to_dict(self) -> Dict[str, Dict[str, str | EmailStr]]:
        return {
            "input": {
                "displayName": self.display_name,
                "email": self.email,
                "password": self.password,
            }
        }


@dataclass(frozen=True)
class LoginUserVariables:
    email: str
    password: str

    def to_dict(self) -> Dict[str, Dict[str, str | EmailStr]]:
        return {
            "input": {
                "email": self.email,
                "password": self.password,
            }
        }


@dataclass(frozen=True)
class VerifyUserEmailVariables:
    verify_email_token: str

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "input": {
                "verifyEmailToken": self.verify_email_token
            }
        }


@dataclass(frozen=True)
class SendVerifyEmailMessageVariables:
    email: str

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "input": {
                "email": self.email
            }
        }


@dataclass(frozen=True)
class SendForgetPasswordMessageVariables:
    email: str

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "input": {
                "email": self.email,
            }
        }


@dataclass(frozen=True)
class ChangePasswordVariables:
    old_password: str
    new_password: str

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "input": {
                "oldPassword": self.old_password,
                "newPassword": self.new_password,
            }
        }


@dataclass(frozen=True)
class ForgetPasswordVariables:
    forget_password_token: str
    new_password: str

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "input": {
                "forgetPasswordToken": self.forget_password_token,
                "newPassword": self.new_password,
            }
        }


@dataclass(frozen=True)
class UpdateUserProfileVariables:
    display_name: Optional[str]
    phone: Optional[str]
    telegram: Optional[str]
    avatar: Optional[BinaryIO]

    def to_dict(self) -> Dict[str, Dict[str, Optional[str | BinaryIO]]]:
        return {
            "input": {
                "displayName": self.display_name,
                "phone": self.phone,
                "telegram": self.telegram,
                "avatar": self.avatar,
            }
        }


@dataclass(frozen=True)
class UpdateMasterVariables:
    id: int
    info: Optional[str]

    def to_dict(self) -> Dict[str, Dict[str, Optional[str]]]:
        return {
            "input": {
                "id": str(self.id),
                "info": self.info,
            }
        }


@dataclass(frozen=True)
class RegisterMasterVariables:
    info: Optional[str]

    def to_dict(self) -> Dict[str, Dict[str, Optional[str]]]:
        return {
            "input": {
                "info": self.info,
            }
        }


@dataclass(frozen=True)
class GetMasterByUserVariables:
    id: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "userId": str(self.id)
        }


@dataclass(frozen=True)
class GetUserByIDVariables:
    id: int

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": str(self.id)
        }


@dataclass(frozen=True)
class GetUserByEmailVariables:
    email: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "email": self.email
        }


@dataclass(frozen=True)
class ToysCatalogVariables:
    limit: int
    offset: int
    filters: ToysFilters

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, Union[str, float, None, bool, int, List[int]]]]]:
        return {
            "input": {
                "pagination": {
                    "limit": self.limit,
                    "offset": self.offset,
                },
                "filters": {
                    "search": self.filters.search,
                    "priceCeil": self.filters.price_ceil,
                    "priceFloor": self.filters.price_floor,
                    "quantityFloor": self.filters.quantity_floor,
                    "categoryID": self.filters.category_id,
                    "tagIDs": self.filters.tags_id,
                    "createdAtOrderByAsc": self.filters.created_at_order_by_asc,
                }
            }
        }


@dataclass(frozen=True)
class ToyByIDVariables:
    id: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "id": self.id,
        }
