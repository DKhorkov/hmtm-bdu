from dataclasses import dataclass
from typing import Optional

from src.core.common.dto import BoolResponse
<<<<<<<< HEAD:src/domains/profile/core/dto.py
from src.domains.profile.core.schemas import Master
========
from src.domains.profile.schemas import Master
>>>>>>>> main:src/domains/profile/dto.py


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
