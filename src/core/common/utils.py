from typing import Optional

from cryptography.fernet import Fernet
from fastapi import Request

from src.core.common.constants import DEFAULT_ERROR_MESSAGE, REQUEST_ENVIRONMENTS_MAPPING


class Cryptography:
    def __init__(self, secret_key: str):
        self.__cipher = Fernet(key=secret_key)

    def encrypt(self, key: str) -> str:
        return self.__cipher.encrypt(key.encode("utf-8")).decode("utf-8")

    def decrypt(self, key: str) -> Optional[str]:
        try:
            return self.__cipher.decrypt(key.encode("utf-8")).decode("utf-8")

        except Exception:
            return None


class Extract:

    @staticmethod
    def error_from_url(request: Request, cryptography: Cryptography) -> Optional[str]:
        error_key: Optional[str] = request.query_params.get("error")

        if not error_key:
            return None

        return REQUEST_ENVIRONMENTS_MAPPING.get(cryptography.decrypt(error_key), DEFAULT_ERROR_MESSAGE)  # type: ignore

    @staticmethod
    def success_message_from_url(request: Request, cryptography: Cryptography) -> Optional[str]:
        message_key: Optional[str] = request.query_params.get("message")

        if not message_key:
            return None

        return REQUEST_ENVIRONMENTS_MAPPING.get(cryptography.decrypt(message_key), DEFAULT_ERROR_MESSAGE)  # type: ignore
