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
