from typing import Dict
from pydantic import EmailStr
from dataclasses import dataclass


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
class UserVerifyEmailVariables:
    verify_email_token: str

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {
            "input": {
                "verifyEmailToken": self.verify_email_token
            }
        }
