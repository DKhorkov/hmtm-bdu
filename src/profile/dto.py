from dataclasses import dataclass
from typing import Optional

from src.common.dto import BoolResponse
from src.profile.models import Master


@dataclass
class UpdateUserProfileResponse(BoolResponse):
    pass


@dataclass
class ChangePasswordResponse(BoolResponse):
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
