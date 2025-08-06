from dataclasses import dataclass
from typing import Optional, BinaryIO, Dict


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
