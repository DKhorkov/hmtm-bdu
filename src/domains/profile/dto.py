from dataclasses import dataclass
from typing import Optional

from src.core.common.dto import BoolResponse
from src.domains.profile.schemas import Master


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
