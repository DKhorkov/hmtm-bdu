from os import getenv
from typing import Dict, Any, Optional

from cryptography.fernet import Fernet
from dotenv import load_dotenv, find_dotenv

from starlette.requests import Request

from src.common.constants import DEFAULT_ERROR_MESSAGE, REQUEST_ENVIRONMENTS_MAPPING

from src.common.datetime_parser import DatetimeParser
from src.common.models import User


def user_from_dict(user_data: Dict[str, Any]) -> User:
    return User(
        id=user_data["id"],
        display_name=user_data["displayName"],
        email=user_data["email"],
        email_confirmed=user_data["emailConfirmed"],
        phone=user_data["phone"],
        phone_confirmed=user_data["phoneConfirmed"],
        telegram=user_data["telegram"],
        telegram_confirmed=user_data["telegramConfirmed"],
        avatar=user_data["avatar"],
        created_at=DatetimeParser.parse(user_data["createdAt"]),
        updated_at=DatetimeParser.parse(user_data["updatedAt"]),
    )


class FernetEnvironmentsKey:
    load_dotenv(find_dotenv('.env.prod'))

    def __init__(self):
        self.__FERNET_KEY: str = getenv("FERNET_KEY", default=Fernet.generate_key().decode("utf8"))

        self.__cipher = Fernet(self.__FERNET_KEY)

    def encrypt(self, key: str) -> str:
        """ Шифрования ключей """
        encrypted_bytes: bytes = self.__cipher.encrypt(key.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, key: str) -> Optional[str]:
        """ Дешифрование ключей """
        try:
            decrypted_bytes: bytes = self.__cipher.decrypt(key.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")

        except Exception:
            return None


def extract_url_error_message(request: Request) -> Optional[str]:
    error_code: Optional[str] = request.query_params.get("error")
    if error_code:
        encrypted_error: FernetEnvironmentsKey = FernetEnvironmentsKey()
        decrypted_error_key: Optional[str] = encrypted_error.decrypt(error_code)

        return REQUEST_ENVIRONMENTS_MAPPING.get(decrypted_error_key, DEFAULT_ERROR_MESSAGE)  # type: ignore[arg-type]

    return None


def extract_url_success_status_message(request: Request) -> Optional[str]:
    status_message: Optional[str] = request.query_params.get("message")
    if status_message:
        encrypted_status: FernetEnvironmentsKey = FernetEnvironmentsKey()
        decrypted_status_key: Optional[str] = encrypted_status.decrypt(status_message)

        return REQUEST_ENVIRONMENTS_MAPPING.get(decrypted_status_key, DEFAULT_ERROR_MESSAGE)  # type: ignore[arg-type]

    return None


async def encryptor() -> FernetEnvironmentsKey:
    return FernetEnvironmentsKey()
